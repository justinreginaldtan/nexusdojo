import sys
import tempfile
from pathlib import Path
import unittest
import os

# Ensure the src directory is importable when running `python -m unittest`.
REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from nexusdojo import cli  # noqa: E402  # Imported after sys.path adjustment.


class TestCLI(unittest.TestCase):
    def test_parser_has_commands(self):
        parser = cli.build_parser()
        args = parser.parse_args(["hello"])
        self.assertEqual(args.command, "hello")

    def test_hello_command_runs(self):
        exit_code = cli.main(["hello"])
        self.assertEqual(exit_code, 0)

    def test_init_creates_workspace(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir)
            exit_code = cli.main(["init", "--path", tmpdir])
            self.assertEqual(exit_code, 0)
            self.assertTrue((target / "knowledge_base").exists())
            self.assertTrue((target / "scratchpad").exists())

    def test_prompt_reads_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt_file = Path(tmpdir) / "prompt.md"
            prompt_file.write_text("test prompt")
            exit_code = cli.main(["prompt", "--file", str(prompt_file)])
            self.assertEqual(exit_code, 0)

    def test_api_dry_run_requires_env(self):
        os.environ["NEXUSDOJO_API_KEY"] = "test-key"
        exit_code = cli.main(["api-dry-run", "--message", "hi"])
        self.assertEqual(exit_code, 0)

    def test_start_log_brief_flow(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            kata_root = Path(tmpdir) / "dojo_root"
            notes_root = Path(tmpdir) / "notes_root"
            exit_code = cli.main(
                [
                    "start",
                    "Sample Kata",
                    "--template",
                    "script",
                    "--root",
                    str(kata_root),
                    "--force",
                ]
            )
            self.assertEqual(exit_code, 0)
            slug_dir = kata_root / "sample-kata"
            self.assertTrue(slug_dir.exists())

            exit_code = cli.main(
                [
                    "log",
                    "sample-kata",
                    "--note",
                    "Did a thing",
                    "--root",
                    str(kata_root),
                    "--notes-root",
                    str(notes_root),
                ]
            )
            self.assertEqual(exit_code, 0)
            self.assertTrue((slug_dir / "LOG.md").exists())
            self.assertTrue((notes_root / "log.md").exists())

            exit_code = cli.main(
                [
                    "brief",
                    "--since",
                    "2000-01-01",
                    "--root",
                    str(kata_root),
                    "--notes-root",
                    str(notes_root),
                ]
            )
            self.assertEqual(exit_code, 0)
            self.assertTrue((notes_root / "briefs").exists())

    def test_dashboard_runs_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            kata_root = Path(tmpdir) / "dojo_root"
            notes_root = Path(tmpdir) / "notes_root"
            exit_code = cli.main(
                [
                    "dashboard",
                    "--root",
                    str(kata_root),
                    "--notes-root",
                    str(notes_root),
                ]
            )
            self.assertEqual(exit_code, 0)

    def test_start_seeds_tests(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            kata_root = Path(tmpdir) / "dojo_root"
            notes_root = Path(tmpdir) / "notes_root"
            exit_code = cli.main(
                [
                    "start",
                    "Script Kata",
                    "--template",
                    "script",
                    "--root",
                    str(kata_root),
                    "--notes-root",
                    str(notes_root),
                    "--tests",
                    "edge",
                    "--force",
                ]
            )
            self.assertEqual(exit_code, 0)
            tests_dir = kata_root / "script-kata" / "tests"
            self.assertTrue((tests_dir / "test_smoke.py").exists())
            self.assertTrue((tests_dir / "test_edge_cases.py").exists())

    def test_continue_uses_latest_activity(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            kata_root = Path(tmpdir) / "dojo_root"
            notes_root = Path(tmpdir) / "notes_root"
            cli.main(
                [
                    "start",
                    "Sample Kata",
                    "--template",
                    "script",
                    "--root",
                    str(kata_root),
                    "--notes-root",
                    str(notes_root),
                    "--force",
                ]
            )
            cli.main(
                [
                    "log",
                    "sample-kata",
                    "--note",
                    "First log line",
                    "--root",
                    str(kata_root),
                    "--notes-root",
                    str(notes_root),
                ]
            )
            exit_code = cli.main(
                [
                    "continue",
                    "--root",
                    str(kata_root),
                    "--notes-root",
                    str(notes_root),
                ]
            )
            self.assertEqual(exit_code, 0)

    def test_hint_dry_run(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            kata_root = Path(tmpdir) / "dojo_root"
            notes_root = Path(tmpdir) / "notes_root"
            project_dir = kata_root / "sample-kata"
            project_dir.mkdir(parents=True, exist_ok=True)
            (project_dir / "README.md").write_text("# Sample Kata -- spec")
            exit_code = cli.main(
                [
                    "hint",
                    "sample-kata",
                    "--root",
                    str(kata_root),
                    "--notes-root",
                    str(notes_root),
                    "--dry-run",
                ]
            )
            self.assertEqual(exit_code, 0)

    def test_test_hints_offline(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            kata_root = Path(tmpdir) / "dojo_root"
            notes_root = Path(tmpdir) / "notes_root"
            project_dir = kata_root / "sample-kata"
            project_dir.mkdir(parents=True, exist_ok=True)
            (project_dir / "README.md").write_text("# Sample Kata -- spec")
            exit_code = cli.main(
                [
                    "test-hints",
                    "sample-kata",
                    "--root",
                    str(kata_root),
                    "--notes-root",
                    str(notes_root),
                    "--offline",
                ]
            )
            self.assertEqual(exit_code, 0)
            self.assertTrue((project_dir / "tests" / "test_edge_hints.py").exists())

    def test_start_avoids_slug_collision(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            kata_root = Path(tmpdir) / "dojo_root"
            notes_root = Path(tmpdir) / "notes_root"
            existing = kata_root / "sample-kata"
            existing.mkdir(parents=True, exist_ok=True)
            (existing / "README.md").write_text("# Existing")
            exit_code = cli.main(
                [
                    "start",
                    "Sample Kata",
                    "--template",
                    "script",
                    "--root",
                    str(kata_root),
                    "--notes-root",
                    str(notes_root),
                    "--yes",
                ]
            )
            self.assertEqual(exit_code, 0)
            self.assertTrue((kata_root / "sample-kata-2").exists())


if __name__ == "__main__":
    unittest.main()
