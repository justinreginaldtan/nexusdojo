import unittest
from unittest import mock
import main


class EdgeCases(unittest.TestCase):
    def test_routes_weather_prompt(self) -> None:
        with mock.patch.object(main, "get_weather", return_value={"city": "Paris", "temp": 20}) as gw:
            result = main.route_prompt("What's the weather in Paris?")
            gw.assert_called_once()
            self.assertEqual(result, {"city": "Paris", "temp": 20})

    def test_routes_news_prompt(self) -> None:
        with mock.patch.object(main, "get_news", return_value=["story"]) as gn:
            result = main.route_prompt("Give me news about AI")
            gn.assert_called_once()
            self.assertEqual(result, ["story"])

    def test_unknown_prompt_raises(self) -> None:
        with self.assertRaises(ValueError):
            main.route_prompt("tell me a joke")
