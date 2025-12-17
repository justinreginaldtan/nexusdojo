import unittest
from main import greet

class MissionTests(unittest.TestCase):
    def test_greet_name(self):
        self.assertEqual(greet("Justin"), "Hello, Justin!")

    def test_greet_empty(self):
        self.assertEqual(greet(""), "Hello, World!")

    def test_greet_none(self):
        self.assertEqual(greet(None), "Hello, World!")
