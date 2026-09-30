import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "mediq.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'patient',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create Doctors table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialization TEXT NOT NULL,
            hospital TEXT NOT NULL,
            rating REAL NOT NULL,
            experience INTEGER NOT NULL,
            fee INTEGER NOT NULL,
            consultation_time TEXT NOT NULL,
            room_number TEXT NOT NULL,
            photo TEXT,
            bio TEXT,
            available_tokens_count INTEGER DEFAULT 20
        )
    ''')

    # Create Symptoms table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS symptoms (
            symptom_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            specialization TEXT NOT NULL,
            is_emergency INTEGER DEFAULT 0
        )
    ''')

    # Create Bookings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_ref TEXT UNIQUE NOT NULL,
            user_id INTEGER,
            patient_name TEXT NOT NULL,
            doctor_id INTEGER NOT NULL,
            token_number INTEGER NOT NULL,
            booking_date TEXT NOT NULL,
            session TEXT DEFAULT 'Morning (9:00 AM - 1:00 PM)',
            status TEXT DEFAULT 'Booked',
            estimated_time TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (doctor_id) REFERENCES doctors (doctor_id)
        )
    ''')

    # Create Queue table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS queues (
            queue_id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_id INTEGER UNIQUE NOT NULL,
            current_token INTEGER DEFAULT 0,
            avg_consultation_time INTEGER DEFAULT 7,
            status TEXT DEFAULT 'Active',
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (doctor_id) REFERENCES doctors (doctor_id)
        )
    ''')

    # Seed symptoms if empty
    cursor.execute("SELECT COUNT(*) FROM symptoms")
    if cursor.fetchone()[0] == 0:
        symptoms_data = [
            # General Symptoms
            ("Fever", "General", "General Medicine", 0),
            ("Fatigue / Weakness", "General", "General Medicine", 0),
            ("Body Pain", "General", "General Medicine", 0),
            ("Chills", "General", "General Medicine", 0),
            ("Dizziness", "General", "General Medicine", 0),
            ("Headache", "General", "General Medicine", 0),

            # Respiratory Symptoms
            ("Cough", "Respiratory", "General Medicine", 0),
            ("Cold", "Respiratory", "General Medicine", 0),
            ("Sore Throat", "Respiratory", "General Medicine", 0),
            ("Runny Nose", "Respiratory", "General Medicine", 0),
            ("Breathing Difficulty", "Respiratory", "General Medicine", 1), # Emergency
            ("Chest Congestion", "Respiratory", "General Medicine", 0),

            # Stomach and Digestive
            ("Stomach Pain", "Stomach & Digestive", "Gastroenterology", 0),
            ("Nausea", "Stomach & Digestive", "Gastroenterology", 0),
            ("Vomiting", "Stomach & Digestive", "Gastroenterology", 0),
            ("Diarrhea", "Stomach & Digestive", "Gastroenterology", 0),
            ("Constipation", "Stomach & Digestive", "Gastroenterology", 0),
            ("Acidity / Heartburn", "Stomach & Digestive", "Gastroenterology", 0),
            ("Loss of Appetite", "Stomach & Digestive", "Gastroenterology", 0),

            # Skin Symptoms
            ("Skin Rash", "Skin", "Dermatology", 0),
            ("Itching", "Skin", "Dermatology", 0),
            ("Skin Redness", "Skin", "Dermatology", 0),
            ("Skin Swelling", "Skin", "Dermatology", 0),
            ("Acne", "Skin", "Dermatology", 0),
            ("Skin Infection", "Skin", "Dermatology", 0),

            # Heart and Circulation
            ("Chest Pain", "Heart & Circulation", "Cardiology", 1), # Emergency
            ("Fast / Irregular Heartbeat", "Heart & Circulation", "Cardiology", 1), # Emergency
            ("Leg Swelling", "Heart & Circulation", "Cardiology", 0),

            # Bone and Muscle
            ("Joint Pain", "Bone & Muscle", "Orthopedics", 0),
            ("Back Pain", "Bone & Muscle", "Orthopedics", 0),
            ("Muscle Pain", "Bone & Muscle", "Orthopedics", 0),
            ("Neck Pain", "Bone & Muscle", "Orthopedics", 0),
            ("Difficulty Moving", "Bone & Muscle", "Orthopedics", 0),

            # Eye Symptoms
            ("Eye Pain", "Eye", "Ophthalmology", 0),
            ("Red Eyes", "Eye", "Ophthalmology", 0),
            ("Blurred Vision", "Eye", "Ophthalmology", 0),
            ("Eye Irritation", "Eye", "Ophthalmology", 0),

            # Ear, Nose & Throat
            ("Ear Pain", "ENT", "ENT", 0),
            ("Hearing Difficulty", "ENT", "ENT", 0),
            ("Sinus Problem", "ENT", "ENT", 0),
            ("Throat Pain", "ENT", "ENT", 0),
            ("Difficulty Swallowing", "ENT", "ENT", 0),

            # Neurological Symptoms
            ("Severe Headache", "Neurological", "Neurology", 0),
            ("Numbness", "Neurological", "Neurology", 1),
            ("Tingling", "Neurological", "Neurology", 0),
            ("Tremors", "Neurological", "Neurology", 0),
            ("Balance Problems", "Neurological", "Neurology", 0),

            # Dental Symptoms
            ("Toothache", "Dental", "Dentistry", 0),
            ("Gum Pain", "Dental", "Dentistry", 0),
            ("Gum Swelling", "Dental", "Dentistry", 0),
            ("Tooth Sensitivity", "Dental", "Dentistry", 0),

            # Urinary Symptoms
            ("Painful Urination", "Urinary", "Urology", 0),
            ("Frequent Urination", "Urinary", "Urology", 0),
            ("Blood in Urine", "Urinary", "Urology", 1)
        ]
        cursor.executemany("INSERT INTO symptoms (name, category, specialization, is_emergency) VALUES (?, ?, ?, ?)", symptoms_data)

    # Seed doctors if empty
    cursor.execute("SELECT COUNT(*) FROM doctors")
    if cursor.fetchone()[0] == 0:
        doctors_data = [
            ("Dr. Anil Kumar", "General Medicine", "City Care Hospital", 4.9, 12, 300, "09:00 AM - 01:00 PM", "Room 102", "https://images.unsplash.com/photo-1622253692010-333f2da6031d?w=300", "Senior General Physician specializing in infectious diseases, chronic illness management, and preventative healthcare.", 16),
            ("Dr. Rahul Menon", "General Medicine", "Apex Health Clinic", 4.7, 10, 250, "10:00 AM - 02:00 PM", "Room 105", "https://images.unsplash.com/photo-1537368910025-700350fe46c7?w=300", "Consultant Physician with extensive experience in family medicine and lifestyle disorders.", 18),
            ("Dr. Arun Das", "General Medicine", "Metro Hospital", 4.5, 8, 300, "02:00 PM - 06:00 PM", "Room 201", "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=300", "Experienced general physician providing comprehensive diagnostic care and fever management.", 12),
            ("Dr. Suresh Kumar", "General Medicine", "City Care Hospital", 4.3, 6, 200, "09:00 AM - 01:00 PM", "Room 104", "https://images.unsplash.com/photo-1582750433449-648ed127bb54?w=300", "General practitioner dedicated to outpatient care and primary medical consultations.", 15),

            ("Dr. Priya Nair", "Cardiology", "Heart & Vascular Care", 4.9, 15, 600, "09:30 AM - 01:30 PM", "Room 301", "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=300", "Lead Cardiologist specialing in preventive cardiology, hypertension, and heart rhythm management.", 10),
            ("Dr. Vikram Sharma", "Cardiology", "City Care Hospital", 4.8, 14, 500, "11:00 AM - 04:00 PM", "Room 303", "https://images.unsplash.com/photo-1594824813566-78853a4f6d35?w=300", "Interventional Cardiologist expert in clinical heart evaluations and coronary health.", 12),

            ("Dr. Sneha Reddy", "Dermatology", "Skin & Aesthetics Clinic", 4.8, 9, 400, "10:00 AM - 03:00 PM", "Room 204", "https://images.unsplash.com/photo-1594824813566-78853a4f6d35?w=300", "Expert Dermatologist specializing in allergy treatments, skin rashes, acne, and cosmetic skin care.", 14),
            ("Dr. Rajesh Varma", "Dermatology", "Skin Care Center", 4.6, 11, 350, "04:00 PM - 08:00 PM", "Room 205", "https://images.unsplash.com/photo-1537368910025-700350fe46c7?w=300", "Dermatologist with over a decade of experience in dermatological infections and laser therapies.", 10),

            ("Dr. Meera Nambiar", "Dentistry", "Bright Smiles Dental Clinic", 4.9, 8, 300, "09:00 AM - 01:00 PM", "Dental Suite 1", "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=300", "Dental surgeon specializing in painless root canals, tooth extractions, and cosmetic dentistry.", 15),
            ("Dr. Kevin Joseph", "Dentistry", "City Care Hospital", 4.7, 6, 250, "02:00 PM - 06:00 PM", "Dental Suite 2", "https://images.unsplash.com/photo-1622253692010-333f2da6031d?w=300", "General dentist skilled in preventive oral care, gum disease treatments, and dental cleanings.", 20),

            ("Dr. Suresh Babu", "Ophthalmology", "Vision Care Institute", 4.8, 16, 450, "09:00 AM - 01:00 PM", "Eye Clinic 1", "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=300", "Senior Ophthalmologist expert in vision correction, cataract evaluation, and glaucoma therapy.", 14),
            ("Dr. Ananya Sen", "Ophthalmology", "City Care Hospital", 4.6, 7, 350, "02:00 PM - 06:00 PM", "Eye Clinic 2", "https://images.unsplash.com/photo-1594824813566-78853a4f6d35?w=300", "Eye Specialist focused on pediatric ophthalmology, corneal infections, and refractive checks.", 16),

            ("Dr. Manoj Pillai", "Orthopedics", "OrthoCare Hospital", 4.8, 13, 500, "10:00 AM - 02:00 PM", "Room 401", "https://images.unsplash.com/photo-1582750433449-648ed127bb54?w=300", "Orthopedic Surgeon expert in joint pain, fracture management, and sports medicine.", 10),
            ("Dr. Deepak Varma", "Orthopedics", "Metro Hospital", 4.6, 9, 400, "03:00 PM - 07:00 PM", "Room 402", "https://images.unsplash.com/photo-1537368910025-700350fe46c7?w=300", "Consultant Orthopedist specializing in spine health, osteoarthritis, and joint rehabilitation.", 12),

            ("Dr. Kavita Rao", "ENT", "ENT Care Center", 4.7, 10, 350, "09:30 AM - 01:30 PM", "ENT Suite 1", "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=300", "Ear, Nose, and Throat Specialist treating sinus disorders, hearing loss, and tonsillitis.", 15),
            ("Dr. Sanjeev Kumar", "ENT", "Apex Health Clinic", 4.5, 7, 300, "03:00 PM - 07:00 PM", "ENT Suite 2", "https://images.unsplash.com/photo-1622253692010-333f2da6031d?w=300", "ENT Surgeon expert in vertiginous conditions, throat pain, and nasal endoscopy.", 18),

            ("Dr. Siddharth Roy", "Neurology", "Neuro Care Center", 4.9, 18, 700, "10:00 AM - 02:00 PM", "Room 501", "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=300", "Chief Neurologist specializing in migraine treatment, neuropathies, and stroke rehabilitation.", 8),

            ("Dr. Arvind Swamy", "Gastroenterology", "Gastro Health Clinic", 4.8, 14, 550, "09:00 AM - 01:00 PM", "Room 208", "https://images.unsplash.com/photo-1582750433449-648ed127bb54?w=300", "Consultant Gastroenterologist treating digestive disorders, IBS, gastritis, and liver diseases.", 12),

            ("Dr. Harish Prasad", "Urology", "Urology Specialty Clinic", 4.7, 11, 500, "11:00 AM - 03:00 PM", "Room 310", "https://images.unsplash.com/photo-1537368910025-700350fe46c7?w=300", "Urologist expert in kidney stone management, urinary tract infections, and prostate care.", 14)
        ]
        cursor.executemany('''
            INSERT INTO doctors (name, specialization, hospital, rating, experience, fee, consultation_time, room_number, photo, bio, available_tokens_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', doctors_data)

    # Initialize queues for all doctors if not already present
    cursor.execute("SELECT doctor_id FROM doctors")
    doctors = cursor.fetchall()
    for doc in doctors:
        doc_id = doc["doctor_id"]
        # Set a realistic starting current_token between 15 and 24 so live queues look active!
        initial_token = 24 if doc_id == 1 else 10 + (doc_id * 2) % 15
        cursor.execute('''
            INSERT OR IGNORE INTO queues (doctor_id, current_token, avg_consultation_time, status)
            VALUES (?, ?, 7, 'Active')
        ''', (doc_id, initial_token))

    # Seed initial demo user
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO users (name, email, phone, password, role)
            VALUES ('Rahul Sharma', 'rahul@example.com', '9876543210', 'password123', 'patient')
        ''')
        cursor.execute('''
            INSERT INTO users (name, email, phone, password, role)
            VALUES ('Dr. Anil Kumar', 'anil@easymed.com', '9876543211', 'doctor123', 'doctor')
        ''')

    # Seed sample active booking for demonstration if empty
    cursor.execute("SELECT COUNT(*) FROM bookings")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO bookings (booking_ref, user_id, patient_name, doctor_id, token_number, booking_date, session, status, estimated_time)
            VALUES ('EM-2026-3101', 1, 'Rahul Sharma', 1, 31, '2026-09-30', 'Morning (9:00 AM - 1:00 PM)', 'Booked', '10:42 AM')
        ''')

    conn.commit()
    conn.close()
    print("Database initialized and seeded successfully.")

if __name__ == "__main__":
    init_db()
