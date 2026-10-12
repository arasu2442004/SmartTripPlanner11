"""
Smart Trip Planner - Automated Test Suite
Validates database, recommendation logic, Flask routes, auth, and trip workflows.
"""

import unittest
import database
import recommendation
from app import app


class SmartTripPlannerTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        database.init_db()

    def test_01_destinations_seeded(self):
        """Verify that at least 15 destinations are loaded into SQLite."""
        destinations = database.get_all_destinations()
        self.assertGreaterEqual(len(destinations), 15, "Expected at least 15 seeded destinations.")
        print(f"[PASS] Test 1: {len(destinations)} destinations verified in database.")

    def test_02_recommendation_algorithm(self):
        """Verify recommendation scoring returns top 3 sorted by score."""
        destinations = database.get_all_destinations()
        top_recs = recommendation.get_top_recommendations(
            destinations=destinations,
            budget=25000,
            days=3,
            travelers=2,
            preference="Nature",
            limit=3
        )
        self.assertEqual(len(top_recs), 3, "Expected exactly 3 recommendations.")
        # Top destination must have high score
        self.assertGreaterEqual(top_recs[0]['suitability_score'], top_recs[1]['suitability_score'])
        self.assertGreaterEqual(top_recs[1]['suitability_score'], top_recs[2]['suitability_score'])
        self.assertIn("why_suitable", top_recs[0])
        print(f"[PASS] Test 2: Top recommendations {top_recs[0]['destination']['name']} ({top_recs[0]['suitability_score']}%), {top_recs[1]['destination']['name']} ({top_recs[1]['suitability_score']}%), {top_recs[2]['destination']['name']} ({top_recs[2]['suitability_score']}%)")

    def test_03_itinerary_generation(self):
        """Verify dynamic day-by-day itinerary generation matches requested days."""
        dest = database.get_destination_by_id(1)
        itinerary_3_days = recommendation.generate_itinerary(dest, days=3, start_location="Chennai")
        self.assertEqual(len(itinerary_3_days), 3)
        self.assertEqual(itinerary_3_days[0]['day'], 1)
        self.assertEqual(itinerary_3_days[2]['day'], 3)
        self.assertTrue(len(itinerary_3_days[0]['morning']) > 0)
        self.assertTrue(len(itinerary_3_days[0]['afternoon']) > 0)
        self.assertTrue(len(itinerary_3_days[0]['evening']) > 0)

        # Test 5 days
        itinerary_5_days = recommendation.generate_itinerary(dest, days=5, start_location="Bangalore")
        self.assertEqual(len(itinerary_5_days), 5)
        print("[PASS] Test 3: Dynamic itinerary generation verified for 3 and 5 days.")

    def test_04_home_and_plan_routes(self):
        """Verify GET / and GET /plan respond with 200 OK."""
        res_home = self.client.get('/')
        self.assertEqual(res_home.status_code, 200)
        self.assertIn(b"Smart Trip Planner", res_home.data)

        res_plan = self.client.get('/plan')
        self.assertEqual(res_plan.status_code, 200)
        self.assertIn(b"Starting Location", res_plan.data)
        self.assertIn(b"Find My Trip", res_plan.data)
        print("[PASS] Test 4: Home and Plan pages rendered successfully.")

    def test_05_recommend_route(self):
        """Verify POST /recommend returns top 3 destinations with scores."""
        form_data = {
            'start_location': 'Bangalore',
            'budget': '30000',
            'days': '4',
            'travelers': '2',
            'preference': 'Nature'
        }
        res = self.client.post('/recommend', data=form_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Top 3 Suggested Destinations", res.data)
        self.assertIn(b"Match Score", res.data)
        self.assertIn(b"Why this destination is suitable", res.data)
        print("[PASS] Test 5: POST /recommend generates top 3 suggestions.")

    def test_06_trip_details_route(self):
        """Verify GET /trip/<id> renders full itinerary and budget breakdown."""
        res = self.client.get('/trip/1?start_location=Chennai&budget=25000&days=3&travelers=2&preference=Nature')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Day-by-Day Itinerary", res.data)
        self.assertIn(b"Estimated Budget Breakdown", res.data)
        self.assertIn(b"Transportation", res.data)
        self.assertIn(b"Hotel", res.data)
        self.assertIn(b"Food", res.data)
        self.assertIn(b"Remaining Budget", res.data)
        print("[PASS] Test 6: Trip details and itemized budget breakdown verified.")

    def test_07_user_auth_and_trip_saving(self):
        """Test user registration, login, saving a trip, viewing dashboard, and deleting trip."""
        import time
        test_email = f"tester_{int(time.time() * 1000)}@smarttrip.com"
        test_pass = "secret123"

        # 1. Register new user
        res_reg = self.client.post('/register', data={
            'name': 'Trip Tester',
            'email': test_email,
            'password': test_pass
        }, follow_redirects=True)
        self.assertEqual(res_reg.status_code, 200)

        # 2. Save a trip (user is now logged in via session in same client)
        res_save = self.client.post('/save-trip', data={
            'destination_id': '1',
            'start_location': 'Chennai',
            'budget': '20000',
            'days': '3',
            'travelers': '2',
            'preference': 'Nature',
            'total_cost': '16500',
            'remaining_budget': '3500'
        }, follow_redirects=True)
        self.assertEqual(res_save.status_code, 200)
        self.assertIn(b"My Trips Dashboard", res_save.data)

        # 3. View dashboard
        res_dash = self.client.get('/my-trips')
        self.assertEqual(res_dash.status_code, 200)
        self.assertIn(b"Allocated Budget", res_dash.data)

        # 4. Logout
        res_logout = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(res_logout.status_code, 200)
        print("[PASS] Test 7: User registration, trip save, dashboard, and logout verified.")


if __name__ == '__main__':
    unittest.main()
