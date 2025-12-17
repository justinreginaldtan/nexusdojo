import unittest
from unittest.mock import Mock
import main


class MissionTests(unittest.TestCase):
    def test_heads_and_tails_paths(self):
        always_heads = Mock(return_value="Heads")
        always_tails = Mock(return_value="Tails")
        self.assertEqual(main.coin_flip(random_choice=always_heads), "Heads")
        self.assertEqual(main.coin_flip(random_choice=always_tails), "Tails")

    def test_invalid_random_choice_value_raises(self):
        bad_random = Mock(return_value="Edge")
        with self.assertRaises(ValueError):
            main.coin_flip(random_choice=bad_random)

    def test_log_path_errors_are_wrapped(self):
        always_heads = Mock(return_value="Heads")
        # Provide a path in a missing directory to trigger an I/O error.
        with self.assertRaises(ValueError):
            main.coin_flip(random_choice=always_heads, log_path="/nonexistent/path/coin.txt")
