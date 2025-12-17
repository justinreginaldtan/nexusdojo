import unittest
import main
from tempfile import TemporaryDirectory
from pathlib import Path


class MissionTests(unittest.TestCase):
    def test_setup_creates_files(self):
        with TemporaryDirectory() as tmpdir:
            created = main.setup_project_structure(tmpdir)
            self.assertIsInstance(created, list)
            self.assertTrue(all(Path(p).exists() for p in created))

    def test_define_interfaces_normalizes(self):
        spec = {"User": {"create": "POST /users", "get": "GET /users/{id}"}}
        normalized = main.define_interfaces(spec)
        self.assertIn("User", normalized)
        self.assertIn("create", normalized["User"])
        self.assertEqual(normalized["User"]["create"], "POST /users")

    def test_write_tests_returns_string(self):
        interfaces = {"User": {"create": "POST /users"}}
        code = main.write_tests(interfaces)
        self.assertIsInstance(code, str)
        self.assertIn("User", code)
