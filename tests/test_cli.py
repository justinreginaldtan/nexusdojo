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


if __name__ == "__main__":
    unittest.main()
