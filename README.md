# EASY MED

**Smart Doctor Recommendation, Digital Token Booking and Queue Management System**

---

## 🌟 Overview

**EASY MED** is a comprehensive healthcare web application that simplifies finding the right doctor, booking digital consultation tokens, and tracking live consultation queues in real time.

Built using **Python (Flask)**, **Scikit-Learn ML Engine**, **SQLite**, and modern **Responsive UI**, EASY MED eliminates physical waiting room congestion by allowing patients to monitor their live turn and estimated consultation time remotely.

---

## 🚀 Key Features

1. **Categorized Symptom Selection**
   - 11 medical symptom categories (General, Respiratory, Stomach & Digestive, Skin, Heart & Circulation, Bone & Muscle, Eye, ENT, Neurological, Dental, Urinary).
   - Multi-select interactive pills with search filter and live counter.

2. **AI/ML Doctor Recommendation Engine**
   - Uses **TF-IDF Vectorization** and **Multinomial Naive Bayes** to analyze symptom combinations and predict the exact doctor specialization with confidence percentages and reasoning summaries.

3. **Emergency Warning System**
   - Instantly detects high-risk symptoms (e.g., severe chest pain, breathing difficulty, numbness) and triggers an **Emergency Alert Modal** advising immediate emergency medical services (108/112).

4. **Doctor Recommendation & Multi-Criteria Sorting**
   - View recommended doctors filtered by department.
   - Sort doctors by **Highest Rating (⭐)**, **Lowest Consultation Fee (₹)**, **Years of Experience**, or **Available Tokens**.

5. **Digital Token Booking**
   - Select consultation date and morning/afternoon sessions.
   - Auto-generates sequential digital consultation tokens (e.g., `Token 31`, `Token 32`) with printable digital token cards and unique booking reference codes.

6. **Real-Time Queue Status Tracker**
   - Displays the **Currently Consulting Token** (animated pulse indicator), **Your Token Number**, **Patients Ahead**, and **Estimated Waiting Time (Minutes)**.
   - Dynamic formula: $\text{Patients Ahead} = \text{User Token} - \text{Current Token} - 1$
   - $\text{Estimated Wait} = \text{Patients Ahead} \times \text{Average Consultation Time}$.
   - Live timeline breakdown with auto-polling real-time updates every 5 seconds.

7. **Doctor & Receptionist Queue Management Portal**
   - Admin desk for hospital staff to click **"CALL NEXT TOKEN"** or **"PREVIOUS TOKEN"**, instantly advancing the queue and recalculating waiting times for all queued patients.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.11, Flask, Flask-CORS
- **AI/ML**: Scikit-Learn (TF-IDF + Naive Bayes Classifier), Pandas, NumPy
- **Database**: SQLite (`mediq.db`) with 5 relational tables: `users`, `doctors`, `symptoms`, `bookings`, `queues`
- **Frontend**: HTML5, CSS3 (Glassmorphism, CSS Variables, Flexbox/Grid), Vanilla JavaScript (Async Fetch API, Auto-polling)

---

## 📁 Directory Structure

```
EASY MED/
├── app.py                # Flask application & REST API endpoints
├── database.py           # SQLite database schema setup & initial seed data
├── ml_engine.py          # Machine learning model for symptom classification
├── README.md             # Project documentation
├── templates/
│   └── index.html        # Main HTML web interface
└── static/
    ├── css/
    │   └── styles.css    # Responsive medical UI styling
    └── js/
        └── app.js        # Frontend application logic & live queue tracker
```

---

## 💻 How to Run the Application

1. **Activate Environment & Install Dependencies**:
   ```bash
   pip install flask flask-cors scikit-learn pandas numpy
   ```

2. **Initialize Database & Train ML Model**:
   ```bash
   python database.py
   python ml_engine.py
   ```

3. **Start Flask Web Server**:
   ```bash
   python app.py
   ```

4. **Access Web Application**:
   Open your browser and navigate to:
   [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 📷 Key User Workflows

```
Symptom Selection ➔ AI Analysis ➔ Specialization Recommendation ➔ Sort & Select Doctor ➔ Book Token ➔ Track Live Queue Status ➔ Doctor Consultation
```
