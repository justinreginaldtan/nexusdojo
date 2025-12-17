"""Behavioral tests for Weather + News Agent."""

import unittest

import main


class AgentTests(unittest.TestCase):
    def test_weather_route(self) -> None:
        self.assertTrue(hasattr(main, "route_prompt"))
        result = main.route_prompt("What's the weather in Paris?")
        self.assertIsInstance(result, dict)
        self.assertEqual(result.get("tool_used"), "get_weather")
        self.assertIn("data", result)

    def test_news_route(self) -> None:
        result = main.route_prompt("Give me news about AI")
        self.assertEqual(result.get("tool_used"), "get_news")
        self.assertIsInstance(result.get("data"), list)

    def test_refusal_on_unknown(self) -> None:
        result = main.route_prompt("Sing me a song")
        self.assertIn("error", result)


if __name__ == "__main__":
    unittest.main()
