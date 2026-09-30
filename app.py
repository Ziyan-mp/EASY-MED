import os
import sqlite3
import datetime
# pyrefly: ignore [missing-import]
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from database import get_db_connection, init_db
from ml_engine import recommend_specialization

app = Flask(__name__)
CORS(app)

# Ensure database is initialized
init_db()

def calculate_waiting_time(current_token, user_token, avg_time_per_patient=7):
    """
    Calculates patients ahead and estimated waiting time in minutes.
    Formula from spec:
    Patients Ahead = user_token - current_token - 1
    Estimated Wait Time = Patients Ahead * avg_consultation_time
    """
    if user_token <= current_token:
        return {
            "patients_ahead": 0,
            "estimated_wait_minutes": 0,
            "status": "Consulted" if user_token < current_token else "Currently Consulting"
        }
    
    patients_ahead = user_token - current_token - 1
    if patients_ahead < 0:
        patients_ahead = 0
        
    estimated_minutes = patients_ahead * avg_time_per_patient
    
    # Calculate estimated consultation clock time
    now = datetime.datetime.now()
    est_completion = now + datetime.timedelta(minutes=estimated_minutes)
    est_time_str = est_completion.strftime("%I:%M %p")
    
    return {
        "patients_ahead": patients_ahead,
        "estimated_wait_minutes": estimated_minutes,
        "estimated_consultation_time": est_time_str,
        "status": "Waiting"
    }

@app.route("/")
def index():
    return render_template("index.html")

# ==================== API ENDPOINTS ====================

@app.route("/api/symptoms", methods=["GET"])
def get_symptoms():
    """Retrieve all symptoms grouped by category."""
    conn = get_db_connection()
    symptoms = conn.execute("SELECT * FROM symptoms ORDER BY category, name").fetchall()
    conn.close()

    categories = {}
    for s in symptoms:
        cat = s["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append({
            "id": s["symptom_id"],
            "name": s["name"],
            "specialization": s["specialization"],
            "is_emergency": bool(s["is_emergency"])
        })
    
    return jsonify({"success": True, "categories": categories})

@app.route("/api/recommend", methods=["POST"])
def recommend_doctor():
    """AI/ML endpoint to analyze selected symptoms and suggest doctor specialization."""
    data = request.json or {}
    selected_symptoms = data.get("symptoms", [])

    recommendation = recommend_specialization(selected_symptoms)
    
    # Fetch doctors for the recommended specialization
    conn = get_db_connection()
    doctors = conn.execute('''
        SELECT d.*, q.current_token 
        FROM doctors d
        LEFT JOIN queues q ON d.doctor_id = q.doctor_id
        WHERE d.specialization = ?
        ORDER BY d.rating DESC
    ''', (recommendation["recommended_specialization"],)).fetchall()
    conn.close()

    doc_list = [dict(d) for d in doctors]

    return jsonify({
        "success": True,
        "recommendation": recommendation,
        "doctors": doc_list
    })

@app.route("/api/doctors", methods=["GET"])
def get_doctors():
    """Fetch doctors with optional specialization filter and sorting options."""
    specialization = request.args.get("specialization")
    sort_by = request.args.get("sort_by", "rating_desc") # rating_desc, fee_asc, exp_desc, tokens_desc
    search_query = request.args.get("search", "").strip()

    conn = get_db_connection()
    query = '''
        SELECT d.*, q.current_token 
        FROM doctors d
        LEFT JOIN queues q ON d.doctor_id = q.doctor_id
        WHERE 1=1
    '''
    params = []

    if specialization and specialization != "All":
        query += " AND d.specialization = ?"
        params.append(specialization)

    if search_query:
        query += " AND (d.name LIKE ? OR d.hospital LIKE ? OR d.specialization LIKE ?)"
        search_pattern = f"%{search_query}%"
        params.extend([search_pattern, search_pattern, search_pattern])

    # Apply sorting
    if sort_by == "rating_desc":
        query += " ORDER BY d.rating DESC"
    elif sort_by == "fee_asc":
        query += " ORDER BY d.fee ASC"
    elif sort_by == "exp_desc":
        query += " ORDER BY d.experience DESC"
    elif sort_by == "tokens_desc":
        query += " ORDER BY d.available_tokens_count DESC"
    else:
        query += " ORDER BY d.rating DESC"

    doctors = conn.execute(query, params).fetchall()
    conn.close()

    return jsonify({"success": True, "doctors": [dict(d) for d in doctors]})

@app.route("/api/doctors/<int:doctor_id>", methods=["GET"])
def get_doctor_details(doctor_id):
    """Retrieve detailed info for a specific doctor including current queue status."""
    conn = get_db_connection()
    doctor = conn.execute('''
        SELECT d.*, q.current_token, q.avg_consultation_time, q.status as queue_status
        FROM doctors d
        LEFT JOIN queues q ON d.doctor_id = q.doctor_id
        WHERE d.doctor_id = ?
    ''', (doctor_id,)).fetchone()

    if not doctor:
        conn.close()
        return jsonify({"success": False, "message": "Doctor not found"}), 404

    # Get highest booked token number for today
    max_token_row = conn.execute('''
        SELECT MAX(token_number) as max_token
        FROM bookings
        WHERE doctor_id = ?
    ''', (doctor_id,)).fetchone()
    
    conn.close()

    doc_dict = dict(doctor)
    current_tok = doc_dict.get("current_token", 0)
    max_tok = max_token_row["max_token"] if max_token_row["max_token"] else current_tok
    
    # Calculate next available token
    next_token = max_tok + 1 if max_tok >= current_tok else current_tok + 1
    
    doc_dict["next_available_token"] = next_token
    doc_dict["token_range"] = f"{next_token} - {next_token + doc_dict['available_tokens_count']}"

    return jsonify({"success": True, "doctor": doc_dict})

@app.route("/api/book-token", methods=["POST"])
def book_token():
    """Book a new consultation token for a patient."""
    data = request.json or {}
    user_id = data.get("user_id", 1)
    patient_name = data.get("patient_name", "Rahul Sharma")
    doctor_id = data.get("doctor_id")
    booking_date = data.get("booking_date", datetime.date.today().strftime("%Y-%m-%d"))
    session = data.get("session", "Morning (9:00 AM - 1:00 PM)")

    if not doctor_id:
        return jsonify({"success": False, "message": "Doctor ID is required"}), 400

    conn = get_db_connection()
    
    # Get doctor details & queue
    doctor = conn.execute("SELECT * FROM doctors WHERE doctor_id = ?", (doctor_id,)).fetchone()
    queue = conn.execute("SELECT * FROM queues WHERE doctor_id = ?", (doctor_id,)).fetchone()

    if not doctor or not queue:
        conn.close()
        return jsonify({"success": False, "message": "Doctor or Queue record not found"}), 404

    current_tok = queue["current_token"]

    # Get max token booked for this doctor
    max_token_row = conn.execute('''
        SELECT MAX(token_number) as max_token
        FROM bookings
        WHERE doctor_id = ? AND booking_date = ?
    ''', (doctor_id, booking_date)).fetchone()

    max_tok = max_token_row["max_token"] if max_token_row and max_token_row["max_token"] else current_tok
    token_number = max_tok + 1 if max_tok >= current_tok else current_tok + 1

    # Calculate wait stats
    wait_info = calculate_waiting_time(current_tok, token_number, queue["avg_consultation_time"])

    # Generate unique booking reference
    booking_ref = f"EM-{datetime.date.today().strftime('%Y%m%d')}-{doctor_id}{token_number:02d}"

    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO bookings (booking_ref, user_id, patient_name, doctor_id, token_number, booking_date, session, status, estimated_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'Booked', ?)
    ''', (booking_ref, user_id, patient_name, doctor_id, token_number, booking_date, session, wait_info["estimated_consultation_time"]))
    
    booking_id = cursor.lastrowid

    # Decrement available tokens count in doctors table
    cursor.execute('''
        UPDATE doctors 
        SET available_tokens_count = MAX(0, available_tokens_count - 1)
        WHERE doctor_id = ?
    ''', (doctor_id,))

    conn.commit()

    # Fetch newly created booking details
    booking = conn.execute('''
        SELECT b.*, d.name as doctor_name, d.specialization, d.hospital, d.room_number, d.fee
        FROM bookings b
        JOIN doctors d ON b.doctor_id = d.doctor_id
        WHERE b.booking_id = ?
    ''', (booking_id,)).fetchone()
    
    conn.close()

    booking_dict = dict(booking)
    booking_dict.update(wait_info)
    booking_dict["current_token"] = current_tok

    return jsonify({"success": True, "booking": booking_dict})

@app.route("/api/my-tokens", methods=["GET"])
def get_my_tokens():
    """Retrieve active bookings and live queue tracking metrics for user."""
    user_id = request.args.get("user_id", 1)
    conn = get_db_connection()

    bookings = conn.execute('''
        SELECT b.*, d.name as doctor_name, d.specialization, d.hospital, d.room_number, d.fee, d.photo,
               q.current_token, q.avg_consultation_time, q.status as queue_status
        FROM bookings b
        JOIN doctors d ON b.doctor_id = d.doctor_id
        LEFT JOIN queues q ON b.doctor_id = q.doctor_id
        WHERE b.user_id = ?
        ORDER BY b.booking_id DESC
    ''', (user_id,)).fetchall()

    conn.close()

    results = []
    for b in bookings:
        b_dict = dict(b)
        current_tok = b_dict.get("current_token", 0)
        user_tok = b_dict.get("token_number", 0)
        avg_time = b_dict.get("avg_consultation_time", 7)
        
        wait_info = calculate_waiting_time(current_tok, user_tok, avg_time)
        b_dict.update(wait_info)
        results.append(b_dict)

    return jsonify({"success": True, "bookings": results})

@app.route("/api/queue/<int:doctor_id>", methods=["GET"])
def get_queue_status(doctor_id):
    """Retrieve complete live queue status, current consulting token, and breakdown timeline."""
    conn = get_db_connection()
    doctor = conn.execute("SELECT * FROM doctors WHERE doctor_id = ?", (doctor_id,)).fetchone()
    queue = conn.execute("SELECT * FROM queues WHERE doctor_id = ?", (doctor_id,)).fetchone()

    if not doctor or not queue:
        conn.close()
        return jsonify({"success": False, "message": "Queue not found"}), 404

    # Fetch all bookings for this doctor for today
    bookings = conn.execute('''
        SELECT b.*, u.name as user_name
        FROM bookings b
        LEFT JOIN users u ON b.user_id = u.user_id
        WHERE b.doctor_id = ?
        ORDER BY b.token_number ASC
    ''', (doctor_id,)).fetchall()
    
    conn.close()

    current_tok = queue["current_token"]
    booking_list = [dict(b) for b in bookings]

    # Generate timeline visualization items
    timeline = []
    # If no bookings in DB, generate standard token list around current_tok for demonstration
    all_token_numbers = [b["token_number"] for b in booking_list]
    min_t = min(all_token_numbers) if all_token_numbers else max(1, current_tok - 2)
    max_t = max(all_token_numbers) if all_token_numbers else current_tok + 10
    
    # Ensure current_token range is included
    start_token = max(1, min(min_t, current_tok))
    end_token = max(max_t, current_tok + 8)

    for t in range(start_token, end_token + 1):
        status_label = "Waiting"
        if t < current_tok:
            status_label = "Completed"
        elif t == current_tok:
            status_label = "Currently Consulting"
            
        matching_b = next((b for b in booking_list if b["token_number"] == t), None)
        patient_name = matching_b["patient_name"] if matching_b else f"Patient {t}"

        timeline.append({
            "token_number": t,
            "patient_name": patient_name,
            "status": status_label,
            "is_current": (t == current_tok)
        })

    return jsonify({
        "success": True,
        "doctor": dict(doctor),
        "queue": dict(queue),
        "current_token": current_tok,
        "avg_consultation_time": queue["avg_consultation_time"],
        "timeline": timeline,
        "last_updated": queue["last_updated"]
    })

# ==================== DOCTOR / RECEPTIONIST QUEUE CONTROL APIs ====================

@app.route("/api/queue/<int:doctor_id>/next", methods=["POST"])
def advance_queue(doctor_id):
    """Doctor / Receptionist action: Call next token."""
    conn = get_db_connection()
    queue = conn.execute("SELECT * FROM queues WHERE doctor_id = ?", (doctor_id,)).fetchone()

    if not queue:
        conn.close()
        return jsonify({"success": False, "message": "Queue not found"}), 404

    new_token = queue["current_token"] + 1
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor = conn.cursor()
    cursor.execute('''
        UPDATE queues 
        SET current_token = ?, last_updated = ?
        WHERE doctor_id = ?
    ''', (new_token, now_str, doctor_id))
    
    # Mark completed bookings
    cursor.execute('''
        UPDATE bookings
        SET status = 'Completed'
        WHERE doctor_id = ? AND token_number < ?
    ''', (doctor_id, new_token))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True, 
        "message": f"Queue advanced to Token {new_token}", 
        "current_token": new_token
    })

@app.route("/api/queue/<int:doctor_id>/prev", methods=["POST"])
def prev_queue(doctor_id):
    """Doctor / Receptionist action: Go back to previous token."""
    conn = get_db_connection()
    queue = conn.execute("SELECT * FROM queues WHERE doctor_id = ?", (doctor_id,)).fetchone()

    if not queue:
        conn.close()
        return jsonify({"success": False, "message": "Queue not found"}), 404

    new_token = max(1, queue["current_token"] - 1)
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor = conn.cursor()
    cursor.execute('''
        UPDATE queues 
        SET current_token = ?, last_updated = ?
        WHERE doctor_id = ?
    ''', (new_token, now_str, doctor_id))
    conn.commit()
    conn.close()

    return jsonify({
        "success": True, 
        "message": f"Queue updated to Token {new_token}", 
        "current_token": new_token
    })

@app.route("/api/queue/<int:doctor_id>/set", methods=["POST"])
def set_queue_token(doctor_id):
    """Set queue token directly to a specific value."""
    data = request.json or {}
    token_num = data.get("token_number")
    if token_num is None or token_num < 1:
        return jsonify({"success": False, "message": "Valid token number required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE queues 
        SET current_token = ?, last_updated = CURRENT_TIMESTAMP
        WHERE doctor_id = ?
    ''', (token_num, doctor_id))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": f"Token updated to {token_num}", "current_token": token_num})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
