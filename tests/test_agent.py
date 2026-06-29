import unittest
from agent import build_travel_agent
from agent.state import create_initial_state, update_conversation_history
from agent.tools import weather_api, currency_api, llm_api
import os
from dotenv import load_dotenv

load_dotenv()


class TestPreferenceExtractor(unittest.TestCase):
    def setUp(self):
        self.agent = build_travel_agent()
    
    def test_preference_extraction_basic(self):
        state = create_initial_state()
        state["user_input"] = "I want a romantic 7-day trip to Europe with a medium budget"
        
        result = self.agent.invoke(state)
        
        self.assertIn("preferences", result)
        self.assertIsNotNone(result["preferences"])
        self.assertTrue("budget" in result["preferences"])
        self.assertTrue("duration" in result["preferences"])
        print(f"✓ Test 1 Passed: Basic preference extraction - {result['preferences']}")
    
    def test_preference_extraction_with_interests(self):
        state = create_initial_state()
        state["user_input"] = "Looking for an adventure-filled beach vacation for 10 days, budget-friendly"
        
        result = self.agent.invoke(state)
        
        self.assertIn("preferences", result)
        preferences = result["preferences"]
        self.assertIn("interests", preferences)
        self.assertTrue(len(preferences.get("interests", [])) > 0)
        print(f"✓ Test 2 Passed: Preference extraction with interests - {preferences}")
    
    def test_preference_extraction_default_values(self):
        state = create_initial_state()
        state["user_input"] = "I want to travel somewhere nice"
        
        result = self.agent.invoke(state)
        
        self.assertIn("preferences", result)
        preferences = result["preferences"]
        self.assertIsNotNone(preferences.get("budget"))
        self.assertIsNotNone(preferences.get("duration"))
        print(f"✓ Test 3 Passed: Default preferences assigned - {preferences}")


class TestDestinationFinder(unittest.TestCase):
    def setUp(self):
        self.agent = build_travel_agent()
    
    def test_destination_finding_by_budget(self):
        state = create_initial_state()
        state["user_input"] = "Budget-friendly beach destination for 5 days"
        
        result = self.agent.invoke(state)
        
        self.assertIn("destinations", result)
        self.assertTrue(len(result["destinations"]) > 0)
        self.assertIn("selected_destination", result)
        print(f"✓ Test 4 Passed: Found {len(result['destinations'])} destinations")
        if result["selected_destination"]:
            print(f"  Selected: {result['selected_destination']['name']}, {result['selected_destination']['country']}")
    
    def test_destination_finding_by_interests(self):
        state = create_initial_state()
        state["user_input"] = "7-day cultural trip with historical sites and museums, medium budget"
        
        result = self.agent.invoke(state)
        
        self.assertIn("destinations", result)
        destinations = result["destinations"]
        self.assertTrue(len(destinations) > 0)
        
        has_culture_tag = any("culture" in dest.get("tags", []) or "history" in dest.get("tags", []) 
                              for dest in destinations)
        self.assertTrue(has_culture_tag)
        print(f"✓ Test 5 Passed: Found {len(destinations)} cultural destinations")
        for dest in destinations[:3]:
            print(f"  - {dest['name']}: {', '.join(dest['tags'][:3])}")
    
    def test_destination_comparison(self):
        state = create_initial_state()
        state["user_input"] = "Romantic honeymoon for 10 days, luxury budget"
        
        result = self.agent.invoke(state)
        
        self.assertIn("comparison_destinations", result)
        comparison = result["comparison_destinations"]
        self.assertTrue(len(comparison) >= 1)
        self.assertTrue(len(comparison) <= 3)
        print(f"✓ Test 6 Passed: Generated {len(comparison)} destinations for comparison")


class TestItineraryCreator(unittest.TestCase):
    def setUp(self):
        self.agent = build_travel_agent()
    
    def test_itinerary_creation_complete(self):
        state = create_initial_state()
        state["user_input"] = "5-day beach vacation in Bali with medium budget"
        
        result = self.agent.invoke(state)
        
        self.assertIn("itinerary", result)
        itinerary = result["itinerary"]
        self.assertIn("days", itinerary)
        self.assertEqual(len(itinerary["days"]), 5)
        print(f"✓ Test 7 Passed: Created complete {len(itinerary['days'])}-day itinerary")
        
        for day in itinerary["days"][:2]:
            print(f"  Day {day['day']}: {day['title']}")
            print(f"    Morning: {day['morning']['activity']}")
    
    def test_itinerary_has_budget_breakdown(self):
        state = create_initial_state()
        state["user_input"] = "7-day trip to Paris"
        
        result = self.agent.invoke(state)
        
        self.assertIn("budget_breakdown", result)
        budget = result["budget_breakdown"]
        self.assertIn("total", budget)
        self.assertIn("accommodation", budget)
        self.assertIn("food", budget)
        self.assertIn("activities", budget)
        self.assertIn("transport", budget)
        print(f"✓ Test 8 Passed: Budget breakdown created")
        print(f"  Total: {budget['currency_symbol']}{budget['total']}")
        print(f"  Daily Average: {budget['currency_symbol']}{budget['daily_average']}")
    
    def test_itinerary_includes_weather(self):
        state = create_initial_state()
        state["user_input"] = "3-day weekend trip to Tokyo"
        
        result = self.agent.invoke(state)
        
        self.assertIn("weather_data", result)
        weather = result["weather_data"]
        self.assertIsNotNone(weather)
        self.assertIn("current", weather)
        self.assertIn("forecast", weather)
        print(f"✓ Test 9 Passed: Weather data included")
        print(f"  Current: {weather['current']['temperature']}°C, {weather['current']['condition']}")


class TestFollowUpHandler(unittest.TestCase):
    def setUp(self):
        self.agent = build_travel_agent()
    
    def test_followup_handling(self):
        state = create_initial_state()
        state["user_input"] = "Plan a 5-day trip to Barcelona"
        
        result = self.agent.invoke(state)
        
        result["user_input"] = "What are the best restaurants in this city?"
        result["is_followup"] = True
        
        followup_result = self.agent.invoke(result)
        
        self.assertIn("followup_response", followup_result)
        self.assertIsNotNone(followup_result.get("followup_response"))
        print(f"✓ Test 10 Passed: Follow-up question handled")
        print(f"  Response preview: {followup_result['followup_response'][:100]}...")


class TestExternalAPIs(unittest.TestCase):
    def test_weather_api(self):
        weather = weather_api.get_weather(48.8566, 2.3522, days=7)
        
        self.assertIsNotNone(weather)
        self.assertIn("current", weather)
        self.assertIn("forecast", weather)
        print(f"✓ Test 11 Passed: Weather API working")
        print(f"  Retrieved {len(weather['forecast'])} days of forecast")
    
    def test_currency_api(self):
        rates = currency_api.get_exchange_rates("USD")
        
        self.assertIsNotNone(rates)
        self.assertIn("rates", rates)
        print(f"✓ Test 12 Passed: Currency API working")
        print(f"  Available currencies: {len(rates['rates'])}")
    
    def test_currency_conversion(self):
        converted = currency_api.convert_currency(100, "USD", "EUR")
        
        self.assertIsNotNone(converted)
        self.assertGreater(converted, 0)
        print(f"✓ Test 13 Passed: Currency conversion working")
        print(f"  100 USD = {converted} EUR")


def run_tests():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestPreferenceExtractor))
    suite.addTests(loader.loadTestsFromTestCase(TestDestinationFinder))
    suite.addTests(loader.loadTestsFromTestCase(TestItineraryCreator))
    suite.addTests(loader.loadTestsFromTestCase(TestFollowUpHandler))
    suite.addTests(loader.loadTestsFromTestCase(TestExternalAPIs))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    print("\n" + "="*70)
    print("TRAVEL PLANNER AI - TEST SUITE")
    print("="*70 + "\n")
    
    result = run_tests()
    
    print("\n" + "="*70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print("="*70 + "\n")
