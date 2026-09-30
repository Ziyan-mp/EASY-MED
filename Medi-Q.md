# MEDI-Q

**Smart Doctor Recommendation, Digital Token Booking and Queue Management System**

---

## 1. Introduction

Medi-Q is a smart healthcare assistance and queue management system designed to make the process of finding and consulting a doctor easier for patients.

The application allows patients to select their symptoms from a list of common symptoms. An AI/ML-based recommendation system analyzes the selected symptoms and suggests a suitable doctor specialization.

The application then displays available doctors from that specialization, along with their ratings, experience, consultation fee, hospital, and available tokens. Doctors can be sorted according to their ratings so that patients can easily compare them.

After selecting a doctor, the patient can book a digital consultation token. The patient can then track the live queue and see which token is currently being consulted, how many patients are ahead, and the estimated waiting time for their consultation.

Medi-Q therefore combines:

- Symptom-based doctor recommendation
- Doctor search and filtering
- Doctor rating and sorting
- Digital token booking
- Queue management
- Estimated consultation time

---

## 2. Problem Statement

Patients visiting hospitals and clinics often face several problems.

They may not know:

- Which type of doctor they should consult
- Which department is suitable for their symptoms
- Which doctors are available
- Which doctor has a better rating
- How many patients are waiting
- Which token is currently being consulted
- How long they need to wait

Patients may also have to physically wait in crowded hospital waiting areas.

Medi-Q aims to provide a simple digital solution for these problems.

---

## 3. Proposed System

Medi-Q provides a complete digital process from symptom selection to consultation queue tracking.

The patient can:

1. Open the Medi-Q application.
2. Select their symptoms from predefined options.
3. Submit the selected symptoms.
4. The AI/ML system analyzes the symptoms.
5. The system suggests an appropriate doctor specialization.
6. Suitable doctors are displayed.
7. Doctors can be sorted by rating.
8. The patient selects a doctor.
9. The patient views the doctor's details.
10. The patient books a digital token.
11. The patient receives a token number.
12. The patient opens the Queue Status page.
13. The patient can see the currently consulting token.
14. The patient can see how many patients are ahead.
15. The system estimates the remaining waiting time.
16. The doctor/receptionist updates the queue after each consultation.

---

## 4. Main Application Flow

```
MEDI-Q
   ↓
Home Page
   ↓
Select Symptoms
   ↓
AI / ML Analysis
   ↓
Recommended Specialization
   ↓
Recommended Doctors
   ↓
Sort by Rating
   ↓
Select a Doctor
   ↓
Doctor Details
   ↓
Book Token
   ↓
Booking Confirmation
   ↓
My Token
   ↓
Queue Status
   ↓
Current Token + Waiting Time
   ↓
Queue Automatically Updates
```

---

## 5. Home Page

The Home Page is the starting point of the application.

It can contain:

- Medi-Q logo
- Welcome message
- Find a Doctor
- Select Symptoms
- My Token
- Queue Status
- Search
- Profile

Example:

```
          MEDI-Q

    Your Health, Simplified

      [ Find a Doctor ]

      [ Select Symptoms ]

      [ My Token ]

      [ Queue Status ]
```

---

## 6. Symptom Selection Page

Instead of requiring the patient to type their symptoms, Medi-Q provides selectable symptoms.

The patient can select multiple symptoms that they are experiencing.

This makes the application simple and easy to use.

Example:

```
          MEDI-Q

    What are your symptoms?

     Select all that apply

  [ Fever ]       [ Headache ]

  [ Cough ]       [ Cold ]

  [ Body Pain ]   [ Nausea ]

  [ Joint Pain ]  [ Skin Rash ]

  [ Toothache ]   [ Eye Pain ]

  [ Back Pain ]   [ Sore Throat ]

         Selected: 3

      [ FIND A DOCTOR ]
```

---

## 7. Symptom Categories

### General Symptoms

- Fever
- Fatigue / Weakness
- Body Pain
- Chills
- Dizziness
- Headache

### Respiratory Symptoms

- Cough
- Cold
- Sore Throat
- Runny Nose
- Breathing Difficulty
- Chest Congestion

### Stomach and Digestive Symptoms

- Stomach Pain
- Nausea
- Vomiting
- Diarrhea
- Constipation
- Acidity / Heartburn
- Loss of Appetite

### Skin Symptoms

- Skin Rash
- Itching
- Skin Redness
- Skin Swelling
- Acne
- Skin Infection

### Heart and Circulation Symptoms

- Chest Pain
- Fast / Irregular Heartbeat
- Leg Swelling

### Bone and Muscle Symptoms

- Joint Pain
- Back Pain
- Muscle Pain
- Neck Pain
- Difficulty Moving

### Eye Symptoms

- Eye Pain
- Red Eyes
- Blurred Vision
- Eye Irritation

### Ear, Nose and Throat Symptoms

- Ear Pain
- Hearing Difficulty
- Sinus Problem
- Throat Pain
- Difficulty Swallowing

### Neurological Symptoms

- Severe Headache
- Numbness
- Tingling
- Tremors
- Balance Problems

### Dental Symptoms

- Toothache
- Gum Pain
- Gum Swelling
- Tooth Sensitivity

### Urinary Symptoms

- Painful Urination
- Frequent Urination
- Blood in Urine

---

## 8. AI-Based Doctor Recommendation

After selecting symptoms, the patient clicks **FIND A DOCTOR**.

The selected symptoms are sent to the AI/ML component.

The system analyzes the symptoms and recommends an appropriate doctor specialization.

**Example 1**

```
Selected Symptoms:
  Fever
  Cough
  Sore Throat
       ↓
  AI / ML Analysis
       ↓
Recommended Specialization:
  GENERAL MEDICINE
```

**Example 2**

```
Selected Symptoms:
  Toothache
  Gum Pain
  Gum Swelling
       ↓
  AI / ML Analysis
       ↓
Recommended Specialization:
  DENTIST
```

**Example 3**

```
Selected Symptoms:
  Skin Rash
  Itching
  Skin Redness
       ↓
  AI / ML Analysis
       ↓
Recommended Specialization:
  DERMATOLOGIST
```

---

## 9. AI Implementation

For a simple student project, the AI component can be implemented using a symptom-to-specialization dataset.

Example:

| Selected Symptoms | Recommended Specialization |
|---|---|
| Fever, cough, cold | General Medicine |
| Chest pain, heartbeat problems | Cardiology |
| Skin rash, itching | Dermatology |
| Toothache, gum swelling | Dentistry |
| Eye pain, blurred vision | Ophthalmology |
| Joint pain, bone problems | Orthopedics |
| Ear pain, throat problems | ENT |
| Severe headache, numbness | Neurology |
| Stomach pain, digestive problems | Gastroenterology |
| Urination problems | Urology |

For a more advanced implementation, Python can be used with:

- Pandas
- Scikit-learn
- Natural Language Processing
- TF-IDF
- Logistic Regression
- Naive Bayes

The model can classify the selected symptoms into a suitable doctor specialization.

---

## 10. Doctor Recommendation Page

After identifying the suitable specialization, the system displays available doctors.

Example:

```
RECOMMENDED DOCTORS

General Medicine

Dr. Anil Kumar
⭐ 4.9
12 Years Experience
₹300 Consultation
12 Tokens Available

[ VIEW DOCTOR ]

----------------------------

Dr. Rahul Menon
⭐ 4.7
10 Years Experience
₹250 Consultation
18 Tokens Available

[ VIEW DOCTOR ]

----------------------------

Dr. Arun Das
⭐ 4.5
8 Years Experience
₹300 Consultation
8 Tokens Available

[ VIEW DOCTOR ]
```

---

## 11. Doctor Sorting

Doctors can be sorted according to their ratings.

Example:

```
Sort By:

[ Highest Rating ▼ ]
```

The system displays doctors from the highest rating to the lowest rating.

Example:

```
Dr. Anil Kumar       ⭐ 4.9
Dr. Rahul Menon      ⭐ 4.7
Dr. Arun Das         ⭐ 4.5
Dr. Suresh Kumar     ⭐ 4.3
```

Other possible sorting options are:

- Highest Rating
- Lowest Consultation Fee
- Earliest Availability
- Most Available Tokens

---

## 12. Doctor Details Page

When the patient selects a doctor, the application displays detailed information.

Example:

```
Dr. Anil Kumar

Specialization:
General Medicine

Rating:
⭐ 4.9 / 5

Experience:
12 Years

Hospital:
City Care Hospital

Consultation Fee:
₹300

Consultation Time:
9:00 AM – 1:00 PM

Current Token:
24

Available Tokens:
25 – 40

[ BOOK TOKEN ]
```

---

## 13. Token Booking Page

After selecting a doctor, the patient can book a consultation token.

The page displays:

- Patient name
- Doctor name
- Specialization
- Hospital
- Date
- Consultation session
- Available tokens

Example:

```
BOOK CONSULTATION

Doctor:
Dr. Anil Kumar

Department:
General Medicine

Date:
29 September 2026

Available Tokens:
25 – 40

[ GET TOKEN ]
```

---

## 14. Token Generation

When the patient clicks **GET TOKEN**, the system generates the next available token.

For example:

- Current last token = 30
- New patient requests a token.
- The system generates: **Token 31**

The token is stored in the database.

---

## 15. Booking Confirmation Page

After successful booking:

```
BOOKING CONFIRMED ✓

Doctor:
Dr. Anil Kumar

Department:
General Medicine

Your Token:
31

Date:
29 September 2026

Estimated Consultation:
10:42 AM

[ VIEW QUEUE ]
```

---

## 16. My Token Page

The My Token page displays the patient's active consultation.

Example:

```
MY TOKEN

Doctor:
Dr. Anil Kumar

Department:
General Medicine

Your Token:
31

Current Token:
24

Patients Ahead:
6

Estimated Waiting Time:
42 Minutes

[ VIEW QUEUE ]
```

---

## 17. Queue Status Page

The Queue Status page is one of the main features of Medi-Q.

It allows the patient to track the consultation queue without continuously waiting inside the hospital.

Example:

```
QUEUE STATUS

Dr. Anil Kumar
General Medicine

CURRENTLY CONSULTING

TOKEN 24

─────────────────────

YOUR TOKEN

TOKEN 31

6 Patients Ahead

Estimated Waiting Time

42 Minutes

Estimated Consultation

10:42 AM

─────────────────────

24 → Currently Consulting
25 → Waiting
26 → Waiting
27 → Waiting
28 → Waiting
29 → Waiting
30 → Waiting
31 → YOU

🔄 Queue updates automatically
```

---

## 18. Queue Calculation

The estimated waiting time can be calculated using the current token and the average consultation time.

For example:

- Current Token = 24
- Patient Token = 31
- Average consultation time = 7 minutes

Patients ahead:

```
31 - 24 - 1 = 6
```

Estimated waiting time:

```
6 × 7 = 42 minutes
```

Therefore:

**Estimated Waiting Time = 42 minutes**

When Token 24 is completed, the current token becomes 25.

The system recalculates the waiting time.

---

## 19. Doctor / Admin Queue Management

A separate page can be provided for the doctor or receptionist.

Example:

```
QUEUE MANAGEMENT

CURRENT TOKEN

24

Patient: Rahul

Status: Consulting

[ PREVIOUS TOKEN ]

[ CALL NEXT TOKEN ]

NEXT TOKEN

25

WAITING TOKENS

26  27  28  29  30  31
```

When the doctor completes the current consultation, the receptionist clicks **CALL NEXT TOKEN**.

The current token changes from 24 to 25.

The patient application then receives the updated queue information.

---

## 20. Complete Queue Process

```
Current Token = 24
        ↓
Patient Token = 31
        ↓
6 Patients Ahead
        ↓
Average Consultation = 7 Minutes
        ↓
Estimated Waiting = 42 Minutes
        ↓
Doctor Completes Token 24
        ↓
Admin Clicks NEXT TOKEN
        ↓
Current Token = 25
        ↓
Patients Ahead = 5
        ↓
Estimated Waiting = 35 Minutes
        ↓
Queue Information Updated
```

---

## 21. Emergency Warning

Medi-Q is designed to recommend a suitable type of doctor and manage consultations. It should not be used to diagnose diseases.

If a patient selects potentially serious symptoms such as severe chest pain or severe breathing difficulty, the application should display an emergency warning.

Example:

```
⚠ EMERGENCY WARNING

Some of your selected symptoms may
require immediate medical attention.

Please contact emergency medical
services or visit the nearest
emergency department.

Do not rely only on Medi-Q for
emergency medical decisions.
```

---

## 22. Notification System

The application can notify patients when their turn is approaching.

For example:

```
Your Token: 31

Current Token: 28

2 patients are ahead of you.

Estimated waiting time:
14 minutes
```

Another notification can be:

```
Your consultation is approaching.

Please be ready for your turn.
```

For a simple implementation, these notifications can be displayed inside the application without implementing SMS or push notification services.

---

## 23. Technology Stack

### Frontend

The frontend can be developed using:

- HTML
- CSS
- JavaScript

or:

- React.js

React can be used if the existing Medi-Q website is already developed using React.

### Backend

The backend can be developed using:

- Python
- Flask

Flask handles:

- User requests
- Login
- Doctor information
- Symptom processing
- AI/ML communication
- Token generation
- Booking
- Queue management

### AI / ML

The AI component can use:

- Python
- Pandas
- Scikit-learn
- NLP
- TF-IDF
- Classification algorithms

### Database

For a simple implementation, **SQLite** can be used.

SQLite is suitable for a student project because it is lightweight and does not require a separate database server.

---

## 24. Database Structure

**Users Table**

- user_id
- name
- phone
- email
- password

**Doctors Table**

- doctor_id
- name
- specialization
- hospital
- rating
- experience
- fee
- consultation_time
- available_tokens

**Symptoms Table**

- symptom_id
- symptom
- specialization

**Bookings Table**

- booking_id
- user_id
- doctor_id
- token_number
- date
- status

**Queue Table**

- queue_id
- doctor_id
- current_token
- average_consultation_time

---

## 25. Backend Working

The backend connects the frontend, AI system, database, and queue system.

The basic process is:

```
Patient
   ↓
Frontend
   ↓
Flask Backend
   ↓
AI / ML
   ↓
Doctor Recommendation
   ↓
Database
   ↓
Doctor Selection
   ↓
Token Booking
   ↓
Queue Management
   ↓
Updated Queue
   ↓
Frontend
```

---

## 26. Complete User Journey

**Step 1 – Open Application**
The patient opens Medi-Q.

**Step 2 – Select Symptoms**
The patient selects symptoms from the predefined list.

**Step 3 – Analyze Symptoms**
The patient clicks FIND A DOCTOR.

**Step 4 – AI Recommendation**
The AI analyzes the selected symptoms.

**Step 5 – Doctor Specialization**
The system suggests a suitable specialization.

**Step 6 – View Doctors**
The system displays available doctors from that specialization.

**Step 7 – Sort Doctors**
Doctors can be sorted according to rating, availability, or consultation fee.

**Step 8 – Select Doctor**
The patient selects a doctor.

**Step 9 – View Details**
The patient views the doctor's profile and consultation details.

**Step 10 – Book Token**
The patient books a digital token.

**Step 11 – Confirmation**
The system displays the token number and booking details.

**Step 12 – Queue Status**
The patient opens the Queue Status page.

**Step 13 – Track Queue**
The patient sees the current token and their position.

**Step 14 – Waiting Time**
The system estimates how long the patient needs to wait.

**Step 15 – Queue Update**
The doctor/receptionist updates the current token after each consultation.

**Step 16 – Patient Turn**
When the patient's token is reached, the patient can proceed for consultation.

---

## 27. System Architecture

```
                         MEDI-Q
                            │
             ┌──────────────┴──────────────┐
             │                             │
        PATIENT SIDE                 DOCTOR/ADMIN SIDE
             │                             │
             ↓                             ↓
      Select Symptoms                Manage Queue
             │                             │
             ↓                             │
        AI / ML Analysis                   │
             │                             │
             ↓                             │
   Doctor Specialization                   │
             │                             │
             ↓                             │
    Recommended Doctors                    │
             │                             │
             ↓                             │
       Sort by Rating                      │
             │                             │
             ↓                             │
       Select Doctor                       │
             │                             │
             ↓                             │
       Book Token                          │
             │                             │
             └──────────────┬──────────────┘
                            ↓
                         DATABASE
                            ↓
                     Queue Management
                            ↓
                     Current Token
                            ↓
                  Waiting Time Calculation
                            ↓
                     Patient Queue Page
```

---

## 28. Advantages

- Helps patients identify a suitable doctor specialization.
- Simple symptom selection without typing.
- Provides AI-based doctor recommendations.
- Allows patients to compare doctors.
- Displays doctor ratings.
- Provides digital token booking.
- Reduces unnecessary physical waiting.
- Displays the currently consulting token.
- Shows the number of patients ahead.
- Estimates consultation waiting time.
- Allows doctors/receptionists to manage the queue.
- Simple and user-friendly interface.
- Can be implemented using lightweight technologies.

---

## 29. Future Scope

Future versions of Medi-Q can include:

- Hospital location and navigation
- Multiple hospitals
- Multiple branches
- Online payment
- Digital prescriptions
- Medical history
- SMS notifications
- Push notifications
- Doctor availability synchronization
- Online consultation
- Emergency queue management
- Electronic health records
- Cloud database
- Mobile application
- Hospital analytics

---

## 30. Conclusion

Medi-Q is a smart digital healthcare assistance and queue management system.

The system starts by allowing patients to select their symptoms from a simple list. An AI/ML system analyzes the selected symptoms and recommends an appropriate doctor specialization.

The application then displays suitable doctors and allows patients to compare them using ratings, availability, experience, and consultation fees.

After selecting a doctor, the patient can book a digital token. The Queue Status page then provides live information about the consultation queue, including the currently consulting token, the patient's token, the number of patients ahead, and the estimated waiting time.

The doctor or receptionist can update the current token after each consultation, allowing the queue information to remain updated.

Medi-Q therefore provides a simple end-to-end solution:

**Select Symptoms → AI Recommendation → Find Doctor → Compare Ratings → Book Token → Track Queue → Know Waiting Time → Consultation**
