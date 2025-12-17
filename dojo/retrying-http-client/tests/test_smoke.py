"""Behavioral tests for Retrying HTTP Client."""

import unittest
from unittest import mock

import main


class RetryingClientTests(unittest.TestCase):
    def test_fetch_retries_on_failure(self) -> None:
        self.assertTrue(hasattr(main, "fetch"))
        calls = []

        def fake_get(url, timeout=None):
            calls.append(url)
            raise TimeoutError("boom")

        with mock.patch.object(main, "http_get", fake_get, create=True):
            with self.assertRaises(Exception):
                main.fetch("http://example.com", retries=2, backoff=0)
        self.assertGreaterEqual(len(calls), 2)


if __name__ == "__main__":
    unittest.main()
