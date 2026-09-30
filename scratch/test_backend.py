import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import unittest
import json
import sqlite3
from app import app
from database import init_db, get_db_connection

class EasyMedTestCase(unittest.TestCase):
    def setUp(self):
        init_db()
        self.app = app.test_client()
        self.app.testing = True

    def test_symptoms_endpoint(self):
        response = self.app.get('/api/symptoms')
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('General', data['categories'])
        self.assertIn('Cardiology', [s['specialization'] for s in data['categories'].get('Heart & Circulation', [])])

    def test_recommendation_endpoint(self):
        # Test general medicine
        res = self.app.post('/api/recommend', json={'symptoms': ['Fever', 'Cough', 'Sore Throat']})
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['recommendation']['recommended_specialization'], 'General Medicine')
        self.assertGreater(len(data['doctors']), 0)

        # Test dentist
        res = self.app.post('/api/recommend', json={'symptoms': ['Toothache', 'Gum Pain', 'Gum Swelling']})
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['recommendation']['recommended_specialization'], 'Dentistry')

        # Test dermatology
        res = self.app.post('/api/recommend', json={'symptoms': ['Skin Rash', 'Itching', 'Skin Redness']})
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['recommendation']['recommended_specialization'], 'Dermatology')

    def test_doctors_and_sorting(self):
        res = self.app.get('/api/doctors?specialization=General+Medicine&sort_by=rating_desc')
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        ratings = [d['rating'] for d in data['doctors']]
        self.assertEqual(ratings, sorted(ratings, reverse=True))

    def test_booking_flow_and_queue_advance(self):
        # Book a token for doctor 1 (Dr. Anil Kumar)
        res = self.app.post('/api/book-token', json={
            'user_id': 1,
            'patient_name': 'Test Patient',
            'doctor_id': 1,
            'booking_date': '2026-09-30',
            'session': 'Morning (9:00 AM - 1:00 PM)'
        })
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        booking = data['booking']
        booked_token = booking['token_number']
        self.assertGreater(booked_token, 0)

        # Get queue status
        res_queue = self.app.get('/api/queue/1')
        qdata = json.loads(res_queue.data)
        self.assertTrue(qdata['success'])
        current_token = qdata['current_token']

        # Advance queue
        res_adv = self.app.post('/api/queue/1/next')
        adv_data = json.loads(res_adv.data)
        self.assertTrue(adv_data['success'])
        self.assertEqual(adv_data['current_token'], current_token + 1)

if __name__ == '__main__':
    unittest.main()
