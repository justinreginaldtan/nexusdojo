import unittest
from unittest import mock
import main


class EdgeCases(unittest.TestCase):
    def test_retries_then_succeeds(self) -> None:
        response = mock.Mock(status_code=200, text="ok", json=lambda: {"ok": True})
        calls = [TimeoutError(), TimeoutError(), response]

        def fake_get(url, timeout=None):
            result = calls.pop(0)
            if isinstance(result, Exception):
                raise result
            return result

        with mock.patch.object(main, "requests", create=True) as requests_mod:
            requests_mod.get.side_effect = fake_get
            res = main.fetch("http://example.com", retries=3, backoff=0)
            self.assertEqual(res.status_code, 200)

    def test_exhausts_retries(self) -> None:
        with mock.patch.object(main, "requests", create=True) as requests_mod:
            requests_mod.get.side_effect = TimeoutError("boom")
            with self.assertRaises(TimeoutError):
                main.fetch("http://example.com", retries=2, backoff=0)
