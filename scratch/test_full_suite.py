import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import unittest
import json
from app import app, calculate_waiting_time
from database import init_db

class FullMediQIntegrationTest(unittest.TestCase):
    def setUp(self):
        init_db()
        self.app = app.test_client()
        self.app.testing = True

    def test_calculate_waiting_time(self):
        # Formula: Patients Ahead = user_token - current_token - 1
        # Est wait = 6 * 7 = 42 mins
        res = calculate_waiting_time(24, 31, 7)
        self.assertEqual(res["patients_ahead"], 6)
        self.assertEqual(res["estimated_wait_minutes"], 42)

        # Currently consulting
        res_current = calculate_waiting_time(24, 24, 7)
        self.assertEqual(res_current["patients_ahead"], 0)
        self.assertEqual(res_current["estimated_wait_minutes"], 0)
        self.assertEqual(res_current["status"], "Currently Consulting")

        # Already consulted
        res_consulted = calculate_waiting_time(25, 24, 7)
        self.assertEqual(res_consulted["patients_ahead"], 0)
        self.assertEqual(res_consulted["estimated_wait_minutes"], 0)
        self.assertEqual(res_consulted["status"], "Consulted")

    def test_symptoms_categories_and_emergency_flags(self):
        res = self.app.get('/api/symptoms')
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        categories = data['categories']
        
        # Verify 11 categories present
        expected_categories = [
            "General", "Respiratory", "Stomach & Digestive", "Skin",
            "Heart & Circulation", "Bone & Muscle", "Eye", "ENT",
            "Neurological", "Dental", "Urinary"
        ]
        for cat in expected_categories:
            self.assertIn(cat, categories, f"Category {cat} missing in symptoms database")

        # Check emergency flags
        respiratory = categories["Respiratory"]
        breathing_diff = next(s for s in respiratory if s["name"] == "Breathing Difficulty")
        self.assertTrue(breathing_diff["is_emergency"])

    def test_ai_ml_recommendations(self):
        test_cases = [
            (["Fever", "Cough", "Sore Throat"], "General Medicine"),
            (["Chest Pain", "Fast / Irregular Heartbeat"], "Cardiology"),
            (["Skin Rash", "Itching", "Skin Redness"], "Dermatology"),
            (["Toothache", "Gum Pain", "Gum Swelling"], "Dentistry"),
            (["Eye Pain", "Blurred Vision", "Red Eyes"], "Ophthalmology"),
            (["Joint Pain", "Back Pain", "Muscle Pain"], "Orthopedics"),
            (["Ear Pain", "Sinus Problem", "Throat Pain"], "ENT"),
            (["Severe Headache", "Numbness", "Tingling"], "Neurology"),
            (["Stomach Pain", "Nausea", "Acidity / Heartburn"], "Gastroenterology"),
            (["Painful Urination", "Frequent Urination", "Blood in Urine"], "Urology")
        ]

        for symptoms, expected_spec in test_cases:
            res = self.app.post('/api/recommend', json={'symptoms': symptoms})
            data = json.loads(res.data)
            self.assertTrue(data['success'])
            rec_spec = data['recommendation']['recommended_specialization']
            self.assertEqual(rec_spec, expected_spec, f"For {symptoms}, expected {expected_spec} but got {rec_spec}")
            self.assertGreater(len(data['doctors']), 0)

    def test_doctor_search_filtering_and_sorting(self):
        # Test sorting by fee ASC
        res = self.app.get('/api/doctors?specialization=General+Medicine&sort_by=fee_asc')
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        fees = [d['fee'] for d in data['doctors']]
        self.assertEqual(fees, sorted(fees))

        # Test sorting by experience DESC
        res = self.app.get('/api/doctors?sort_by=exp_desc')
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        exps = [d['experience'] for d in data['doctors']]
        self.assertEqual(exps, sorted(exps, reverse=True))

        # Test search query
        res = self.app.get('/api/doctors?search=Anil')
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertTrue(any("Anil" in d['name'] for d in data['doctors']))

    def test_doctor_details_api(self):
        res = self.app.get('/api/doctors/1')
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        doc = data['doctor']
        self.assertEqual(doc['doctor_id'], 1)
        self.assertIn('next_available_token', doc)
        self.assertIn('token_range', doc)

    def test_complete_booking_and_queue_workflow(self):
        # 1. Book token
        res_book = self.app.post('/api/book-token', json={
            'user_id': 1,
            'patient_name': 'Rahul Sharma',
            'doctor_id': 1,
            'booking_date': '2026-09-30',
            'session': 'Morning (9:00 AM - 1:00 PM)'
        })
        b_data = json.loads(res_book.data)
        self.assertTrue(b_data['success'])
        booking = b_data['booking']
        user_token = booking['token_number']
        
        # 2. Verify My Tokens
        res_my = self.app.get('/api/my-tokens?user_id=1')
        my_data = json.loads(res_my.data)
        self.assertTrue(my_data['success'])
        self.assertGreater(len(my_data['bookings']), 0)
        found = any(b['token_number'] == user_token for b in my_data['bookings'])
        self.assertTrue(found)

        # 3. Check Queue Tracker
        res_q = self.app.get('/api/queue/1')
        q_data = json.loads(res_q.data)
        self.assertTrue(q_data['success'])
        cur_token = q_data['current_token']

        # 4. Advance queue as Doctor/Admin
        res_next = self.app.post('/api/queue/1/next')
        next_data = json.loads(res_next.data)
        self.assertTrue(next_data['success'])
        self.assertEqual(next_data['current_token'], cur_token + 1)

        # 5. Set token directly
        res_set = self.app.post('/api/queue/1/set', json={'token_number': 24})
        set_data = json.loads(res_set.data)
        self.assertTrue(set_data['success'])
        self.assertEqual(set_data['current_token'], 24)

if __name__ == '__main__':
    unittest.main()
