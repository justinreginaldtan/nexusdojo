"""
Command-line interface for the NexusDojo scaffold.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import random
import re
import shlex
import shutil
import sys
import subprocess
import threading
import termios
import time
import urllib.error
import urllib.request
import tty
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Iterable, Optional

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from rich.align import Align
from rich.live import Live
from rich.spinner import Spinner
from rich.text import Text
from rich.tree import Tree
from rich.syntax import Syntax

from . import __version__

# Initialize Rich console
console = Console()
# console._session_start_time = time.time() # For session timer - Temporarily disabled due to issues

# Resolve paths relative to the package installation or repo root
# If installed in editable mode, this points to the repo root.
# __file__ is src/nexusdojo/cli.py
# parents[0] = src/nexusdojo
# parents[1] = src
# parents[2] = repo_root
REPO_ROOT = Path(__file__).resolve().parents[2]

# Default workspace location for local knowledge artifacts.
DEFAULT_WORKSPACE = REPO_ROOT / "nexusdojo_data"
# Default root for dojo katas.
DEFAULT_KATA_ROOT = REPO_ROOT / "dojo"
# Default root for notes and briefs.
DEFAULT_NOTES_ROOT = REPO_ROOT / "notes"
# Location of bundled templates (relative to repo root).
TEMPLATES_ROOT = REPO_ROOT / "templates"
# Default model settings for idea generation.
DEFAULT_IDEA_PROVIDER = "ollama"
DEFAULT_IDEA_MODEL = "qwen2.5-coder:1.5b"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
# Relaxed rate limits (unlimited daily, short debounce)
HINT_COOLDOWN_SECONDS = 5
HINT_MAX_PER_DAY = 9999  # Effectively unlimited


def build_parser() -> argparse.ArgumentParser:
    """
    Build the argument parser with subcommands.
    """
    parser = argparse.ArgumentParser(
        prog="dojo",
        description="Local CLI scaffold for NexusDojo.",
    )
    subparsers = parser.add_subparsers(dest="command", required=False)

    hello_parser = subparsers.add_parser(
        "hello",
        help="Print a quickstart reminder.",
    )
    hello_parser.set_defaults(func=handle_hello)

    info_parser = subparsers.add_parser(
        "info",
        help="Show environment details.",
    )
    info_parser.set_defaults(func=handle_info)

    init_parser = subparsers.add_parser(
        "init",
        help="Create a local workspace skeleton.",
    )
    init_parser.add_argument(
        "--path",
        default=str(DEFAULT_WORKSPACE),
        help="Target directory for knowledge and scratch artifacts.",
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="Allow reuse of a non-empty directory.",
    )
    init_parser.set_defaults(func=handle_init)

    prompt_parser = subparsers.add_parser(
        "prompt",
        help="Display a stored system prompt for reference.",
    )
    prompt_parser.add_argument(
        "--file",
        default="system_prompts/senior_ai_mentor.md",
        help="Path to the prompt file to display.",
    )
    prompt_parser.set_defaults(func=handle_prompt)

    api_parser = subparsers.add_parser(
        "api-dry-run",
        help="Build an API request payload using env vars (no network call).",
    )
    api_parser.add_argument(
        "--provider",
        default="openai",
        choices=["openai", "gemini"],
        help="Target LLM provider for the example payload.",
    )
    api_parser.add_argument(
        "--message",
        default="Hello from NexusDojo",
        help="Message content to include in the payload.",
    )
    api_parser.add_argument(
        "--model",
        default="gpt-4.1-mini",
        help="Model identifier to include in the payload.",
    )
    api_parser.add_argument(
        "--api-key-env",
        default="NEXUSDOJO_API_KEY",
        help="Environment variable name to read the API key from.",
    )
    api_parser.set_defaults(func=handle_api_dry_run)

    start_parser = subparsers.add_parser(
        "start",
        help="Create a new kata from a template.",
    )
    start_parser.add_argument(
        "idea",
        nargs="?",
        help="Short description of what you plan to build. If omitted, the idea picker will propose one.",
    )
    start_parser.add_argument(
        "--template",
        default="script",
        choices=["script", "fastapi", "rag", "mcp"],
        help="Template to use for the new kata (default: script).",
    )
    start_parser.add_argument(
        "--pillar",
        default=None,
        help="Focus pillar to steer the idea picker (python/cli/api/testing/mixed).",
    )
    start_parser.add_argument(
        "--mode",
        default=None,
        help="Mode or template hint (script/api).",
    )
    start_parser.add_argument(
        "--level",
        default=None,
        help="Difficulty hint (foundation/proficient/stretch).",
    )
    start_parser.add_argument(
        "--root",
        default=str(DEFAULT_KATA_ROOT),
        help="Root directory where katas are stored.",
    )
    start_parser.add_argument(
        "--notes-root",
        default=str(DEFAULT_NOTES_ROOT),
        help="Directory for shared notes/logs (used for idea picking).",
    )
    start_parser.add_argument(
        "--force",
        action="store_true",
        help="Allow reusing an existing (empty) kata directory.",
    )
    start_parser.add_argument(
        "--guided",
        action="store_true",
        help="Force the guided start flow with explicit prompts.",
    )
    start_parser.add_argument(
        "--reuse-settings",
        action="store_true",
        help="Reuse the last guided start settings without prompting.",
    )
    start_parser.add_argument(
        "--tests",
        choices=["edge", "smoke", "skip"],
        default=None,
        help="Test scaffolding preference: edge (smoke + TODOs), smoke only, or skip.",
    )
    start_parser.add_argument(
        "--scaffold",
        choices=["auto", "llm", "skip"],
        default="auto",
        help="Bootcamp-style scaffold: auto (LLM when interactive), llm, or skip.",
    )
    start_parser.add_argument(
        "--offline",
        action="store_true",
        help="Skip model calls and use curated offline ideas/scaffolds.",
    )
    start_parser.add_argument(
        "--yes",
        action="store_true",
        help="Auto-confirm the proposed idea without prompting (non-interactive safe).",
    )
    start_parser.set_defaults(func=handle_start)

    refresh_parser = subparsers.add_parser(
        "scaffold-refresh",
        help="Regenerate missing scaffold files for a kata without touching user code.",
    )
    refresh_parser.add_argument(
        "project",
        help="Slug of the kata to refresh.",
    )
    refresh_parser.add_argument(
        "--root",
        default=str(DEFAULT_KATA_ROOT),
        help="Root directory where katas are stored.",
    )
    refresh_parser.set_defaults(func=handle_scaffold_refresh)

    idea_parser = subparsers.add_parser(
        "idea",
        help="Generate kata ideas based on your logs and calibrations.",
    )
    idea_parser.add_argument(
        "--provider",
        default=DEFAULT_IDEA_PROVIDER,
        choices=["ollama", "openrouter"],
        help="LLM provider to use for idea generation.",
    )
    idea_parser.add_argument(
        "--model",
        default=DEFAULT_IDEA_MODEL,
        help="Model identifier to use (default is a fast, low-cost model).",
    )
    idea_parser.add_argument(
        "--root",
        default=str(DEFAULT_KATA_ROOT),
        help="Root directory where katas are stored (for context).",
    )
    idea_parser.add_argument(
        "--notes-root",
        default=str(DEFAULT_NOTES_ROOT),
        help="Directory for shared notes/logs.",
    )
    idea_parser.add_argument(
        "--pillar",
        default=None,
        help="Optional pillar hint for idea generation.",
    )
    idea_parser.add_argument(
        "--level",
        default=None,
        help="Optional level hint (complexity).",
    )
    idea_parser.add_argument(
        "--mode",
        default=None,
        help="Optional mode/template hint.",
    )
    idea_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the prompt context without calling the model.",
    )
    idea_parser.set_defaults(func=handle_idea)

    log_parser = subparsers.add_parser(
        "log",
        help="Record a note for a kata.",
    )
    log_parser.add_argument(
        "project",
        help="Slug of the kata to log against.",
    )
    log_parser.add_argument(
        "--note",
        required=True,
        help="What you accomplished or learned.",
    )
    log_parser.add_argument(
        "--root",
        default=str(DEFAULT_KATA_ROOT),
        help="Root directory where katas are stored.",
    )
    log_parser.add_argument(
        "--notes-root",
        default=str(DEFAULT_NOTES_ROOT),
        help="Directory for shared notes/logs.",
    )
    log_parser.set_defaults(func=handle_log)

    brief_parser = subparsers.add_parser(
        "brief",
        help="Summarize recent logs and write a brief.",
    )
    brief_parser.add_argument(
        "--since",
        help="YYYY-MM-DD cutoff (defaults to last 7 days).",
    )
    brief_parser.add_argument(
        "--root",
        default=str(DEFAULT_KATA_ROOT),
        help="Root directory where katas are stored.",
    )
    brief_parser.add_argument(
        "--notes-root",
        default=str(DEFAULT_NOTES_ROOT),
        help="Directory for shared notes/logs.",
    )
    brief_parser.set_defaults(func=handle_brief)

    calibrate_parser = subparsers.add_parser(
        "calibrate",
        help="Log a quick self-assessment for a skill pillar.",
    )
    calibrate_parser.add_argument(
        "--pillar",
        default="python",
        choices=["python", "cli", "api", "testing"],
        help="Skill pillar to log.",
    )
    calibrate_parser.add_argument(
        "--score",
        type=int,
        choices=range(1, 6),
        required=True,
        help="Score 1-5 (Foundations=1, Proficient=3, Hiring-ready=5).",
    )
    calibrate_parser.add_argument(
        "--note",
        default="",
        help="Optional context about the calibration.",
    )
    calibrate_parser.add_argument(
        "--notes-root",
        default=str(DEFAULT_NOTES_ROOT),
        help="Directory for shared notes/logs.",
    )
    calibrate_parser.set_defaults(func=handle_calibrate)

    dashboard_parser = subparsers.add_parser(
        "dashboard",
        help="Show a session dashboard with progress signals.",
    )
    dashboard_parser.add_argument(
        "--root",
        default=str(DEFAULT_KATA_ROOT),
        help="Root directory where katas are stored.",
    )
    dashboard_parser.add_argument(
        "--notes-root",
        default=str(DEFAULT_NOTES_ROOT),
        help="Directory for shared notes/logs.",
    )
    dashboard_parser.set_defaults(func=handle_dashboard)

    continue_parser = subparsers.add_parser(
        "continue",
        help="Show the most recent kata and next-step hints.",
    )
    continue_parser.add_argument(
        "--root",
        default=str(DEFAULT_KATA_ROOT),
        help="Root directory where katas are stored.",
    )
    continue_parser.add_argument(
        "--notes-root",
        default=str(DEFAULT_NOTES_ROOT),
        help="Directory for shared notes/logs.",
    )
    continue_parser.set_defaults(func=handle_continue)

    transcript_parser = subparsers.add_parser(
        "transcript",
        help="Append a manual transcript or summary note.",
    )
    transcript_parser.add_argument(
        "--text",
        required=True,
        help="Transcript text to record.",
    )
    transcript_parser.add_argument(
        "--summarize",
        action="store_true",
        help="Also write a compact summary line.",
    )
    transcript_parser.add_argument(
        "--notes-root",
        default=str(DEFAULT_NOTES_ROOT),
        help="Directory for shared notes/logs.",
    )
    transcript_parser.set_defaults(func=handle_transcript)

    hint_parser = subparsers.add_parser(
        "hint",
        help="Pull a concise, rate-limited hint for a kata.",
    )
    hint_parser.add_argument(
        "project",
        help="Slug of the kata to get a hint for.",
    )
    hint_parser.add_argument(
        "--question",
        default="",
        help="Optional focus question for the hint.",
    )
    hint_parser.add_argument(
        "--provider",
        default=DEFAULT_IDEA_PROVIDER,
        choices=["ollama", "openrouter"],
        help="LLM provider to use for hints.",
    )
    hint_parser.add_argument(
        "--model",
        default=DEFAULT_IDEA_MODEL,
        help="Model identifier to use.",
    )
    hint_parser.add_argument(
        "--root",
        default=str(DEFAULT_KATA_ROOT),
        help="Root directory where katas are stored.",
    )
    hint_parser.add_argument(
        "--notes-root",
        default=str(DEFAULT_NOTES_ROOT),
        help="Directory for shared notes/logs.",
    )
    hint_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the prompt context without calling the model.",
    )
    hint_parser.add_argument(
        "--offline",
        action="store_true",
        help="Skip model calls and emit a curated fallback hint.",
    )
    hint_parser.set_defaults(func=handle_hint)

    test_hint_parser = subparsers.add_parser(
        "test-hints",
        help="Generate edge-case test TODOs for a kata (skipped tests).",
    )
    test_hint_parser.add_argument(
        "project",
        help="Slug of the kata to target.",
    )
    test_hint_parser.add_argument(
        "--max",
        type=int,
        default=4,
        help="Maximum number of edge-case suggestions to materialize.",
    )
    test_hint_parser.add_argument(
        "--provider",
        default=DEFAULT_IDEA_PROVIDER,
        choices=["ollama", "openrouter"],
        help="LLM provider to use for test hints.",
    )
    test_hint_parser.add_argument(
        "--model",
        default=DEFAULT_IDEA_MODEL,
        help="Model identifier to use.",
    )
    test_hint_parser.add_argument(
        "--root",
        default=str(DEFAULT_KATA_ROOT),
        help="Root directory where katas are stored.",
    )
    test_hint_parser.add_argument(
        "--notes-root",
        default=str(DEFAULT_NOTES_ROOT),
        help="Directory for shared notes/logs.",
    )
    test_hint_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the prompt context without calling the model.",
    )
    test_hint_parser.add_argument(
        "--offline",
        action="store_true",
        help="Skip model calls and use curated edge-case hints.",
    )
    test_hint_parser.set_defaults(func=handle_test_hints)

    # Friendly menu when no command is provided.
    menu_parser = subparsers.add_parser(
        "menu",
        help="Interactive menu for common tasks.",
    )
    menu_parser.set_defaults(func=handle_menu)

    check_parser = subparsers.add_parser(
        "check",
        help="Run tests and get AI feedback.",
    )
    check_parser.add_argument(
        "project",
        nargs="?",
        help="Slug of the kata to check (defaults to current directory).",
    )
    check_parser.add_argument(
        "--root",
        default=str(DEFAULT_KATA_ROOT),
        help="Root directory where katas are stored.",
    )
    check_parser.add_argument(
        "--notes-root",
        default=str(DEFAULT_NOTES_ROOT),
        help="Directory for shared notes/logs.",
    )
    check_parser.set_defaults(func=handle_check)

    watch_parser = subparsers.add_parser(
        "watch",
        help="Continuously run tests on file changes.",
    )
    watch_parser.add_argument(
        "project",
        nargs="?",
        help="Slug of the kata to watch (defaults to current directory).",
    )
    watch_parser.add_argument(
        "--root",
        default=str(DEFAULT_KATA_ROOT),
        help="Root directory where katas are stored.",
    )
    watch_parser.add_argument(
        "--notes-root",
        default=str(DEFAULT_NOTES_ROOT),
        help="Directory for shared notes/logs.",
    )
    watch_parser.set_defaults(func=handle_watch)

    play_parser = subparsers.add_parser(
        "play",
        help="Open a temporary playground for experimentation.",
    )
    play_parser.set_defaults(func=handle_play)

    solve_parser = subparsers.add_parser(
        "solve",
        help="Generate a solution for the current kata (Zero XP).",
    )
    solve_parser.add_argument(
        "project",
        nargs="?",
        help="Slug of the kata to solve.",
    )
    solve_parser.set_defaults(func=handle_solve)

    reset_parser = subparsers.add_parser(
        "reset",
        help="Reset main.py to the initial boilerplate.",
    )
    reset_parser.add_argument(
        "project",
        nargs="?",
        help="Slug of the kata to reset.",
    )
    reset_parser.set_defaults(func=handle_reset)

    return parser


def handle_watch(args: argparse.Namespace) -> int:
    """
    Watch for file changes and auto-run dojo check.
    """
    import time
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    kata_root = Path(args.root).expanduser()
    if args.project:
        project_dir = kata_root / args.project
    else:
        project_dir = Path.cwd()

    if not (project_dir / "tests").exists():
        console.print(f"[bold red]Error:[/bold red] No 'tests' folder found in {project_dir}.")
        return 1

    start_time = time.time()
    last_tick = start_time
    elapsed_seconds = 0.0
    last_status = "Idle"
    last_checked = None
    last_duration = None
    last_failure_detail: Optional[dict[str, str]] = None
    last_failure_sig: Optional[str] = None
    repeat_fail_count = 0
    history: list[str] = []
    sensei_block: Optional[Panel] = None
    live_ref: Optional[Live] = None
    input_mode = False
    running_tests = False
    paused = False
    stop_keys = threading.Event()
    run_lock = threading.Lock()
    toast_msg = ""
    toast_until = 0.0

    def set_toast(msg: str, duration: float = 3.0) -> None:
        """
        Show a short-lived status message without breaking the layout.
        """
        nonlocal toast_msg, toast_until
        toast_msg = msg
        toast_until = time.time() + duration

    def live_pause() -> None:
        if live_ref and hasattr(live_ref, "pause"):
            try:
                live_ref.pause()
            except Exception:
                pass

    def live_resume() -> None:
        if live_ref and hasattr(live_ref, "resume"):
            try:
                live_ref.resume()
            except Exception:
                pass

    def build_banner(elapsed_secs: int, paused_banner: bool) -> Panel:
        mins, secs = divmod(elapsed_secs, 60)
        watch_display = f"Current Kata > {project_dir.name}"
        keys_line = "p: pause   r: run test   a: ask   c: clear   q: quit"
        timer_display = f"{mins:02}:{secs:02}"
        # Build timer string with consistent width for alignment
        if paused_banner:
            # Keep consistent width: "(paused) " is 9 chars
            timer_col = f"[dim](paused) {timer_display}[/dim]"
        else:
            # Pad with spaces to match the width of "(paused) " (9 chars)
            timer_col = f"[dim]         {timer_display}[/dim]"
        grid = Table.grid(expand=True)
        # First row: project name on left, timer on right (matching Sensei Response style)
        grid.add_row(watch_display, timer_col, style="")
        grid.add_row("Edit any .py file to trigger tests.")
        grid.add_row(f"[dim]{keys_line}[/dim]")
        return Panel(
            grid,
            border_style="blue",
            title="[bold]Sensei Watch[/bold]",
            title_align="center",
        )

    def render_status(status: str) -> None:
        """
        Render a single-line status without spamming newlines (Rich-aware).
        """
        console.print(status, end="\r", soft_wrap=False, overflow="crop", highlight=False)
        try:
            console.file.flush()
        except Exception:
            pass

    def parse_failure_summary(output: str) -> dict[str, str]:
        """
        Extract a short failure summary from unittest output.
        """
        lines = output.splitlines()
        test_name = ""
        snippet = ""
        for line in lines:
            if line.startswith(("FAIL:", "ERROR:")):
                test_name = line.split(":", 1)[1].strip()
                break
        file_line = ""
        for line in lines:
            if line.strip().startswith("File ") and ", line " in line:
                file_line = line.strip()
                break
        if not snippet and lines:
            snippet = "\n".join(lines[:4]).strip()
        return {"test": test_name or "unknown", "line": file_line or (lines[0] if lines else ""), "snippet": snippet}

    def update_history(status_char: str) -> None:
        history.append(status_char)
        while len(history) > 6:
            history.pop(0)

    def history_bar() -> str:
        if not history:
            return ""
        return "[" + " ".join(history) + "]"

    def run_single_test(test_name: str) -> int:
        """
        Run a specific test by name inside the project.
        """
        result = subprocess.run(
            [sys.executable, "-m", "unittest", test_name],
            cwd=project_dir,
            capture_output=True,
            text=True,
        )
        output = result.stderr or result.stdout
        style = "green" if result.returncode == 0 else "red"
        console.print(Panel(summarize_failure_output(output), title=f"Test {test_name}", border_style=style))
        return result.returncode

    def build_sensei_hint(question: str, timestamp: str = "") -> Panel:
        """
        Build a short hint using local context (mission + last failure + streak).
        """
        # Build structured content sections
        sections = []

        if question:
            sections.append(f"[bold]Your Question[/bold]\n{question}")

        if last_failure_detail:
            fail_name = last_failure_detail.get("test", "")
            fail_line = last_failure_detail.get("line", "")
            snippet = summarize_text(last_failure_detail.get("snippet", ""), 160)
            fail_info = []
            if fail_name:
                fail_info.append(f"[dim]{fail_name}[/dim]")
            if fail_line:
                fail_info.append(f"[dim]{fail_line}[/dim]")
            if fail_info:
                sections.append(f"[bold]Last Failure[/bold]\n" + "\n".join(fail_info))
            if snippet:
                sections.append(f"[dim]{snippet}[/dim]")

        if history:
            sections.append(f"[bold]Recent Results[/bold]\n{' '.join(history)}")

        # Try LLM-powered guidance first, then fall back to deterministic hints
        guidance = None
        try:
            # Build context for LLM
            context = f"Question: {question}\n"
            if last_failure_detail:
                context += f"Last failure: {last_failure_detail.get('test', 'unknown')}\n"
                context += f"Error: {last_failure_detail.get('snippet', '')[:200]}\n"
            if history:
                context += f"Recent results: {' '.join(history)}\n"
            mission_path = project_dir / "MISSION.md"
            if mission_path.exists():
                context += f"Mission:\n{mission_path.read_text()[:500]}\n"

            system = (
                "You are a helpful coding tutor. Based on the student's question and test failures, "
                "provide 2-3 SHORT, actionable suggestions to help them debug. Be specific and practical. "
                "Focus on what they should check or try next, not the full solution."
            )
            messages = [
                {"role": "system", "content": system},
                {"role": "user", "content": context}
            ]
            guidance = call_idea_api(DEFAULT_IDEA_PROVIDER, DEFAULT_IDEA_MODEL, messages)
        except Exception:
            guidance = None

        if not guidance:
            guidance = fallback_hint(question)

        if guidance:
            cleaned: list[str] = []
            for line in guidance.splitlines():
                if re.search(r"re-?read your question", line, re.IGNORECASE):
                    continue
                clean_line = line.strip()
                # Remove leading dashes/bullets that might be duplicated
                clean_line = re.sub(r"^[\-•]\s*", "", clean_line)
                if clean_line:
                    cleaned.append(clean_line)
            cleaned = [ln for ln in cleaned if ln]
            if cleaned:
                suggestion_lines = "\n".join(f"• {ln}" for ln in cleaned)
                sections.append(f"[bold]Suggestions[/bold]\n{suggestion_lines}")

        body = "\n\n".join(sections)

        # Create panel with title integrated at top
        return Panel(
            body,
            border_style="yellow",
            title="[bold]Sensei Response[/bold]",
            title_align="center",
        )

    def execute_check(single_test: Optional[str] = None) -> None:
        """
        Run either full check or a single test, with state tracking.
        """
        nonlocal last_status, last_checked, last_duration, last_failure_detail, last_failure_sig, repeat_fail_count, running_tests, sensei_block
        if paused or stop_keys.is_set():
            return
        if not run_lock.acquire(blocking=False):
            return
        try:
            running_tests = True
            started_at = time.time()
            # Don't pause Live display - we'll show a loading indicator within it
            if single_test:
                rc = run_single_test(single_test)
                failure_info = None
                output_signature = single_test
            else:
                check_args = argparse.Namespace(**vars(args))
                check_args.auto_log = True
                check_args.collect_failure = True
                result = handle_check(check_args)
                if isinstance(result, tuple):
                    rc, failure_info = result
                else:
                    rc, failure_info = result, None
                output_signature = ""
                if failure_info:
                    output_signature = failure_info.get("test", "") + failure_info.get("line", "")
            last_duration = f"{time.time() - started_at:.1f}s"
            last_status = "Passed" if rc == 0 else "Failed"
            last_checked = datetime.now().strftime("%H:%M:%S")
            update_history("✓" if rc == 0 else "✗")

            if rc != 0:
                detail = None
                if not single_test and failure_info:
                    detail = failure_info
                elif single_test:
                    detail = {"test": single_test, "snippet": "", "line": ""}
                if detail:
                    sig = output_signature or (detail.get("test", "") + detail.get("line", ""))
                    if sig and sig == last_failure_sig:
                        repeat_fail_count += 1
                    else:
                        repeat_fail_count = 1
                        last_failure_sig = sig

                    # Always display failure detail to user
                    snippet = detail.get("snippet", "").strip()
                    name = detail.get("test", "unknown")
                    line = detail.get("line", "")
                    live_pause()
                    console.print(Panel(
                        f"{line}\n\n{snippet}",
                        title=f"❌ Last failing test: {name}",
                        border_style="red",
                    ))
                    live_resume()
                    last_failure_detail = detail
            else:
                repeat_fail_count = 0
                last_failure_detail = None
                last_failure_sig = None
            # Clear sensei block and show result toast
            sensei_block = None
            set_toast(f"✓ Passed" if rc == 0 else "✗ Failed", duration=5.0)
        finally:
            running_tests = False
            run_lock.release()

    def keyboard_listener() -> None:
        """
        Listen for lightweight controls: p=toggle pause, r=run tests, a=ask sensei, c=clear, q=quit.
        """
        nonlocal paused, sensei_block, live_ref, input_mode
        fd = None
        orig_attrs = None
        try:
            fd = sys.stdin.fileno()
            orig_attrs = termios.tcgetattr(fd)
            tty.setcbreak(fd)
        except Exception:
            fd = None
            orig_attrs = None
        try:
            while not stop_keys.is_set():
                try:
                    ch = sys.stdin.read(1)
                except Exception:
                    break
                if not ch:
                    continue
                if ch.lower() == "p":
                    paused = not paused
                elif ch.lower() == "c":
                    console.clear()
                    set_toast("Cleared")
                    sensei_block = None
                elif ch.lower() == "r":
                    execute_check()
                elif ch.lower() == "a":
                    set_toast("Ask Sensei")
                    input_mode = True
                    live_pause()
                    question = Prompt.ask("Ask Sensei (Enter to cancel)", default="")
                    live_resume()
                    input_mode = False
                    if question.strip():
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        # Build hint with timestamp in title
                        hint = build_sensei_hint(question.strip(), timestamp)
                        sensei_block = hint
                        set_toast("Sensei response ready")
                    else:
                        set_toast("Ask cancelled")
                elif ch.lower() == "q":
                    stop_keys.set()
                    observer.stop()
                    break
        finally:
            if orig_attrs and fd is not None:
                try:
                    termios.tcsetattr(fd, termios.TCSADRAIN, orig_attrs)
                except Exception:
                    pass

    class TestRunnerHandler(FileSystemEventHandler):
        def on_modified(self, event):
            nonlocal last_status, last_checked, last_duration
            if event.src_path.endswith(".py"):
                # Small debounce to avoid double-firing on some editors
                time.sleep(0.1)
                if paused or stop_keys.is_set():
                    return
                set_toast(f"Change detected in {Path(event.src_path).name}")
                try:
                    last_status = "Running"
                    execute_check()
                except Exception as e:
                    console.print(f"[red]Error running check: {e}[/red]")

    event_handler = TestRunnerHandler()
    observer = Observer()
    observer.schedule(event_handler, str(project_dir), recursive=True)
    observer.start()

    # Keyboard controls
    key_thread = threading.Thread(target=keyboard_listener, daemon=True)
    key_thread.start()

    try:
        with Live(console=console, refresh_per_second=6, screen=True) as live:
            live_ref = live
            while not stop_keys.is_set():
                now = time.time()
                if not paused:
                    elapsed_seconds += now - last_tick
                last_tick = now
                if input_mode:
                    time.sleep(0.1)
                    continue
                elapsed_display = int(elapsed_seconds)

                # Show loading state while tests are running
                if running_tests:
                    status_renderable = Spinner("dots", text="Running tests...")
                elif last_checked:
                    bar = history_bar()
                    # Format: "Test Passed/Failed (6.9s) at 01:44:18" followed by history bar
                    status_text = "Test Passed" if last_status == "Passed" else "Test Failed"
                    status_line = f"[bold]{status_text}[/bold]"
                    if last_duration:
                        status_line += f" [dim]({last_duration})[/dim]"
                    status_line += f" [dim]at {last_checked}[/dim]"
                    if bar:
                        status_line += f" {bar}"
                    status_renderable = Text.from_markup(status_line or " ", justify="left")
                else:
                    status_renderable = Spinner("dots", text="Listening…")

                toast_line = ""
                if toast_msg and time.time() < toast_until:
                    toast_line = toast_msg
                else:
                    toast_msg = ""
                    toast_until = 0.0

                blocks = [
                    build_banner(elapsed_display, paused),
                    status_renderable,
                ]
                if sensei_block:
                    blocks.append(sensei_block)
                blocks.append(Text(toast_line or " ", style="dim", justify="left"))
                live.update(Group(*blocks))
                time.sleep(0.2 if running_tests else 1.0)
    except KeyboardInterrupt:
        observer.stop()
        console.print("\n[blue]Watch stopped.[/blue]")
    finally:
        # Clear the status line before exit
        console.print(" " * 120, end="\r", soft_wrap=False, overflow="crop", highlight=False)
    observer.join()
    return 0


def handle_check(args: argparse.Namespace) -> int:
    """
    Run tests for a kata, providing visual feedback and AI diagnosis on failure.
    """
    import subprocess

    notes_root = Path(getattr(args, "notes_root", DEFAULT_NOTES_ROOT)).expanduser()
    notes_root.mkdir(parents=True, exist_ok=True)
    kata_root = Path(args.root).expanduser()
    if args.project:
        project_dir = kata_root / args.project
    else:
        project_dir = Path.cwd()

    # Validate we are in a kata
    if not (project_dir / "tests").exists():
        console.print(f"[bold red]Error:[/bold red] No 'tests' folder found in {project_dir}. Are you in a kata directory?")
        return 1
    
    # Auto-install deps
    install_dependencies(project_dir)
    
    # Check for auto-log flag passed via args or inferred
    auto_log = getattr(args, "auto_log", False)

    # In watch mode, suppress verbose output to avoid breaking the Live display
    silent_mode = auto_log

    if not silent_mode:
        console.print(f"[bold blue]Running tests for:[/bold blue] {project_dir.name}...")

    collect_failure = bool(getattr(args, "collect_failure", False))

    # Run unittest
    result = subprocess.run(
        [sys.executable, "-m", "unittest"],
        cwd=project_dir,
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        # Success Case
        if not silent_mode:
            console.print(Panel(
                "[bold green]ALL TESTS PASSED[/bold green]\n\n"
                "Great work, Engineer. The system is stable.",
                title="✅ MISSION COMPLETE",
                border_style="green",
                box=box.DOUBLE
            ))

        # Mark tutorial complete if applicable
        if project_dir.name == "tutorial-hello":
            marker = notes_root / ".tutorial_complete"
            marker.write_text("tutorial complete", encoding="utf-8")
            console.print("[bold green]Tutorial complete! Returning you to the main menu next time.[/bold green]")

        # --- Progression System ---
        kata_meta_path = project_dir / ".kata.json"
        if kata_meta_path.exists():
            try:
                meta = json.loads(kata_meta_path.read_text())
                pillar = meta.get("pillar", "mixed")
                cheated = meta.get("cheated", False)

                if not silent_mode:
                    if cheated:
                        console.print("[dim]XP forfeited (Solution Used).[/dim]")
                    elif not auto_log:
                        console.print(f"[bold]Rate this drill ([cyan]{pillar.upper()}[/cyan]):[/bold]")
                        console.print("[1] Too Easy  (Speed +5 XP)")
                        console.print("[2] Perfect   (Growth +15 XP)")
                        console.print("[3] Too Hard  (Grit +20 XP)")
                        rating = Prompt.ask("Rating", choices=["1", "2", "3"], default="2")
                        xp_gain, new_level = update_skill(Path(args.notes_root), pillar, rating)
                        console.print(Panel(
                            f"XP Gained: [bold gold1]+{xp_gain}[/bold gold1]\n"
                            f"New Level: [bold cyan]{new_level}[/bold cyan]",
                            title="🆙 LEVEL UP",
                            border_style="gold1"
                        ))

                if auto_log and not cheated:
                     # In silent mode, we award standard XP (Perfect=15) silently
                     update_skill(Path(args.notes_root), pillar, "2")

            except Exception as e:
                if not silent_mode:
                    console.print(f"[dim]XP update failed: {e}[/dim]")

        # Auto-log logic
        if auto_log:
            # Silent Log
            note = "Tests passed (Watch Mode Auto-Log)"
            handle_log(argparse.Namespace(
                project=project_dir.name,
                note=note,
                root=str(kata_root),
                notes_root=str(args.notes_root)
            ))
        elif not silent_mode:
            if Confirm.ask("Log this victory?"):
                note = Prompt.ask("What did you learn/build?")
                handle_log(argparse.Namespace(
                    project=project_dir.name,
                    note=note,
                    root=str(kata_root),
                    notes_root=str(args.notes_root)
                ))
        return (0, None) if collect_failure else 0

    else:
        # Failure Case
        error_out = result.stderr or result.stdout

        if not silent_mode:
            # Truncate if huge
            if len(error_out) > 2000:
                error_disp = error_out[:2000] + "\n... (truncated)"
            else:
                error_disp = error_out

            console.print(Panel(
                f"[white]{error_disp.strip()}[/white]",
                title="[bold red]❌ TESTS FAILED[/bold red]",
                border_style="red",
                box=box.HEAVY
            ))

            console.print("\n[bold yellow]Analyzing failure...[/bold yellow]")

            # AI Diagnosis
            diagnosis = get_failure_diagnosis(
                project_dir.name,
                error_out,
                Path(args.notes_root)
            )

            console.print(Panel(
                diagnosis,
                title="🤖 Sensei Diagnosis",
                border_style="yellow",
                padding=(1, 2)
            ))
        else:
            # Still get diagnosis in silent mode for failure_detail collection
            get_failure_diagnosis(
                project_dir.name,
                error_out,
                Path(args.notes_root)
            )
        if collect_failure:
            fail_lines = (error_out or "").splitlines()
            test_name = ""
            first_line = ""
            for line in fail_lines:
                if line.startswith(("FAIL:", "ERROR:")):
                    test_name = line.split(":", 1)[1].strip()
                    break
            for line in fail_lines:
                if line.strip().startswith("File ") and ", line " in line:
                    first_line = line.strip()
                    break
            failure_detail = {
                "test": test_name or "unknown",
                "line": first_line or (fail_lines[0] if fail_lines else ""),
                "snippet": summarize_failure_output(error_out, max_lines=6, max_chars=600),
            }
            return 1, failure_detail
        return 1


# --- Skill / XP System ---

def load_skills(notes_root: Path) -> dict[str, int]:
    path = notes_root / "skills.json"
    if not path.exists():
        return {"python": 0, "cli": 0, "api": 0, "testing": 0, "mixed": 0}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {"python": 0, "cli": 0, "api": 0, "testing": 0, "mixed": 0}

def save_skills(notes_root: Path, skills: dict[str, int]) -> None:
    path = notes_root / "skills.json"
    path.write_text(json.dumps(skills, indent=2))


def format_pillar_label(pillar: str) -> str:
    """
    Normalize pillar labels for display (e.g., CLI, API).
    """
    mapping = {"cli": "CLI", "api": "API", "python": "Python", "testing": "Testing", "mixed": "Mixed"}
    return mapping.get(pillar, pillar.title())


def summarize_failure_output(output: str, max_lines: int = 20, max_chars: int = 1200) -> str:
    """
    Produce a short, readable failure summary to avoid scrollback spam.
    """
    if not output:
        return ""
    lines = output.splitlines()
    trimmed = "\n".join(lines[:max_lines])
    if len(lines) > max_lines:
        trimmed += f"\n... ({len(lines) - max_lines} more lines truncated)"
    if len(trimmed) > max_chars:
        trimmed = trimmed[:max_chars].rstrip() + "\n... (truncated)"
    return trimmed


def is_first_time_user(kata_root: Path, notes_root: Path) -> bool:
    """
    Determine if the user is brand new (no katas/logs and no tutorial marker).
    """
    marker = notes_root / ".tutorial_complete"
    if marker.exists():
        return False
    has_logs = (notes_root / "log.md").exists() and (notes_root / "log.md").stat().st_size > 0
    tutorial_exists = (kata_root / "tutorial-hello").exists()
    has_katas = any((p / "tests").exists() for p in kata_root.iterdir() if p.is_dir())
    if tutorial_exists and not marker.exists():
        return True
    return not has_logs and not has_katas


def ensure_tutorial_kata(kata_root: Path) -> Path:
    """
    Create a minimal tutorial kata if it does not exist.
    """
    tutorial_dir = kata_root / "tutorial-hello"
    tests_dir = tutorial_dir / "tests"
    tutorial_dir.mkdir(parents=True, exist_ok=True)
    tests_dir.mkdir(parents=True, exist_ok=True)

    mission = """Mission: Print a friendly greeting.

Implement main() so it returns the exact string "Hello Dojo".
"""
    readme = "# Tutorial: Hello Dojo\n\nA tiny kata to learn the flow. Edit main.py, run tests, make them pass."
    main_py = """def main():
    \"\"\"Return a friendly greeting.\"\"\"
    # TODO: replace the placeholder with the expected string
    return \"\"


if __name__ == \"__main__\":
    print(main())
"""
    test_main = """import unittest
from main import main


class TestHello(unittest.TestCase):
    def test_greeting(self):
        self.assertEqual(main(), \"Hello Dojo\")


if __name__ == \"__main__\":
    unittest.main()
"""
    (tutorial_dir / "MISSION.md").write_text(mission, encoding="utf-8")
    (tutorial_dir / "README.md").write_text(readme, encoding="utf-8")
    if not (tutorial_dir / "main.py").exists():
        (tutorial_dir / "main.py").write_text(main_py, encoding="utf-8")
    if not (tests_dir / "test_main.py").exists():
        (tests_dir / "test_main.py").write_text(test_main, encoding="utf-8")
    return tutorial_dir


def get_level_info(xp: int) -> tuple[str, str]:
    """Returns (Level Title, Next Level Progress)."""
    if xp < 100:
        return "Novice", f"{xp}/100"
    elif xp < 300:
        return "Apprentice", f"{xp}/300"
    elif xp < 600:
        return "Journeyman", f"{xp}/600"
    elif xp < 1000:
        return "Expert", f"{xp}/1000"
    else:
        return "Master", "MAX"

def update_skill(notes_root: Path, pillar: str, rating: str) -> tuple[int, str]:
    """
    Updates XP based on difficulty rating.
    Rating: 1=Easy, 2=Perfect, 3=Hard.
    Returns (XP Gained, New Level Title).
    """
    skills = load_skills(notes_root)
    current_xp = skills.get(pillar, 0)
    
    # Base XP for completion = 10
    # Modifiers: Easy=+5, Perfect=+15, Hard=+20
    gains = {"1": 15, "2": 25, "3": 30}
    gain = gains.get(rating, 10)
    
    new_xp = current_xp + gain
    skills[pillar] = new_xp
    save_skills(notes_root, skills)
    
    level_title, _ = get_level_info(new_xp)
    return gain, f"{level_title} ({new_xp} XP)"


def get_failure_diagnosis(project_name: str, traceback: str, notes_root: Path) -> str:
    """
    Ask the AI to explain the traceback simply.
    """
    system = (
        "You are a senior python engineer. Analyze the traceback and give a ONE sentence hint "
        "on what might be wrong. Do not give the full code fix. Focus on the logic error."
    )
    user = f"Project: {project_name}\nTraceback:\n{traceback[-2000:]}" # Send last 2000 chars
    
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user}
    ]
    
    # Reuse existing API call logic
    hint = call_idea_api(DEFAULT_IDEA_PROVIDER, DEFAULT_IDEA_MODEL, messages)
    if not hint:
        return "Could not reach the AI for diagnosis. Check the traceback above."
    return hint


def generate_mission_spec(
    project_dir: Path,
    idea_line: str,
    pillar_hint: Optional[str],
    level_hint: Optional[str],
    template: str,
    notes_root: Path,
    offline: bool = False,
) -> tuple[str, list[str], bool]:
    """
    Generate a structured MISSION.md and acceptance criteria using the LLM.
    """
    idea_title = strip_idea_prefix(idea_line)
    
    system = (
        "You are a Senior Product Manager/Architect for an AI solutions company. "
        "Your task is to define a clear mission for a junior engineer. "
        "Return ONLY a JSON object with the following keys:\n"
        "- 'goal': (string) A concise, actionable goal for the project.\n"
        "- 'inputs': (list of strings) Describe any required inputs (e.g., 'A string representing a log line').\n"
        "- 'outputs': (list of strings) Describe expected outputs (e.g., 'A dictionary of parsed log components').\n"
        "- 'constraints': (list of strings) Non-functional requirements like 'Handle all file I/O errors gracefully', 'Ensure type hints are used', 'Must be performant for large inputs'.\n"
        "- 'acceptance_criteria': (list of strings) Short, testable statements like 'Function must return correct value for valid input', 'Function must raise ValueError for invalid input'.\n"
        "Keep it concise, professional, and focus on testable outcomes. No conversational fluff, just JSON."
    )
    user = (
        f"Generate a mission specification for a kata with the following details:\n"
        f"Idea: {idea_title}\n"
        f"Pillar: {pillar_hint or 'unspecified'}\n"
        f"Level: {level_hint or 'unspecified'}\n"
        f"Template: {template}\n"
        "Return JSON only."
    )
    
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user}
    ]
    
    spec_json = None
    fallback_used = False
    if not offline:
        content = call_idea_api(DEFAULT_IDEA_PROVIDER, DEFAULT_IDEA_MODEL, messages)
        if content:
            text = content.strip()
            if "{" in text and "}" in text:
                start = text.find("{")
                end = text.rfind("}")
                if start != -1 and end != -1:
                    text = text[start : end + 1]
            try:
                spec_json = json.loads(text)
            except json.JSONDecodeError:
                preview = (text or content or "")[:200]
                print(f"Error parsing mission spec JSON: {preview}...", file=sys.stderr)

    if not spec_json:
        fallback_used = True
        print("LLM failed to generate mission spec; using deterministic fallback.", file=sys.stderr)
        spec_json = {
            "goal": f"Implement a {idea_title} based on standard Python practices.",
            "inputs": ["Varies by project idea."],
            "outputs": ["Varies by project idea."],
            "constraints": ["Ensure type hints are used.", "Handle edge cases gracefully."],
            "acceptance_criteria": [
                f"Basic functionality for {idea_title} works as expected.",
                "Code adheres to Python best practices (e.g., PEP8).",
            ],
        }

    # Write MISSION.md
    md_lines = [
        f"# Mission: {spec_json.get('goal', idea_title)}",
        "",
        "## Overview",
        spec_json.get("goal", "Implement the core logic for this kata."),
        "",
        "## Inputs",
        *[f"- {i}" for i in spec_json.get("inputs", [])],
        "",
        "## Outputs",
        *[f"- {o}" for o in spec_json.get("outputs", [])],
        "",
        "## Constraints",
        *[f"- {c}" for c in spec_json.get("constraints", [])],
        "",
        "## Acceptance Criteria (Tests)",
        *[f"- {ac}" for ac in spec_json.get("acceptance_criteria", [])],
        "",
        "## Quickstart",
        "1. Read this `MISSION.md` carefully.",
        "2. Implement your solution in `main.py`.",
        "3. Run tests using `dojo check` to verify acceptance criteria.",
        "4. Log your progress: `dojo log <kata-slug> --note \"...\"`",
        "5. Once complete: `dojo check` to pass all tests, then log your victory!",
    ]
    (project_dir / "MISSION.md").write_text("\n".join(md_lines))

    # Write test_mission.py
    acceptance_criteria = spec_json.get("acceptance_criteria", [])
    tests_dir = project_dir / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)
    test_file_path = tests_dir / "test_mission.py"
    
    test_lines = [
        '"""Auto-generated mission tests. Implement these to complete the kata."""',
        "import unittest",
        "import main # Assuming main.py contains your logic",
        "",
        "class MissionTests(unittest.TestCase):",
    ]
    
    for idx, criteria in enumerate(acceptance_criteria):
        safe_criteria = summarize_text(criteria, 80).replace("'", "\"")
        test_lines.extend([
            f"    @unittest.skip(f'TODO: Implement for: {safe_criteria}')",
            f"    def test_acceptance_criteria_{idx + 1}(self):",
            f"        # Test: {criteria}",
            "        self.fail('Test not implemented yet')",
            "",
        ])
    
    # Add a final placeholder test if no criteria were generated
    if not acceptance_criteria:
         test_lines.extend([
            f"    @unittest.skip(f'TODO: Implement mission for: {idea_title}')",
            f"    def test_mission_placeholder(self):",
            f"        self.fail('Mission tests not generated or implemented')",
            "",
        ])
    
    test_file_path.write_text("\n".join(test_lines))

    return "\n".join(md_lines), acceptance_criteria, fallback_used


def handle_hello(_: argparse.Namespace) -> int:
    """
    Print a short quickstart message.
    """
    print("Welcome to the NexusDojo CLI scaffold.")
    print("Next steps: `dojo init` to create a workspace, then wire ingestion/search.")
    return 0


def handle_info(args: argparse.Namespace) -> int:
    """
    Display environment info and allow editing profile settings.
    """
    console.print(Panel(f"NexusDojo CLI v{__version__}", title="System Info", border_style="blue"))
    
    # Environment stats
    table = Table(box=box.SIMPLE)
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="white")
    table.add_row("Python", sys.version.split()[0])
    table.add_row("Platform", platform.platform())
    table.add_row("Working Dir", str(Path.cwd()))
    table.add_row("Kata Root", str(DEFAULT_KATA_ROOT))
    console.print(table)
    console.print()

    # User Settings
    notes_root = getattr(args, "notes_root", str(DEFAULT_NOTES_ROOT))
    if notes_root:
        notes_path = Path(notes_root)
        settings = load_settings(notes_path)
        current_name = settings.get("user_name", "Engineer")
        
        console.print(f"[bold]Current Profile Name:[/bold] {current_name}")
        
        if Confirm.ask("Would you like to change your display name?"):
            new_name = Prompt.ask("Enter new name").strip()
            if new_name:
                settings["user_name"] = new_name
                save_settings(notes_path, settings)
                console.print(f"[green]Name updated to {new_name}.[/green]")
            else:
                console.print("Name unchanged.")
    
    return 0


def handle_help(_: argparse.Namespace) -> int:
    """
    Display the recommended workflow and help guide.
    """
    guide = """
# 🥋 The NexusDojo Workflow

**Goal:** Frictionless training loop to build "Muscle Memory".

### 1. ⚡ Quick Train
Start every session with **[1] Quick Train** from the menu.
The AI analyzes your skills and generates a tailored mission.

### 2. 📜 Read the Mission
Go to the kata folder:
`cd dojo/<kata-slug>`
Read `MISSION.md`. Understand the **Inputs**, **Outputs**, and **Constraints**.

### 3. 👀 Sensei Watch Mode
Open a split pane and run:
`dojo watch`
This will auto-run tests every time you save.

### 4. ⌨️  Code (The Vibe)
Open `main.py` in Neovim.
Write code -> Save -> Green Light.
If Red: Read the AI diagnosis in the watch pane.

### 5. 📝 Log & Level Up
Once passed, the system will ask to log your victory.
Rate the difficulty to adjust future drills:
- **Too Easy:** +5 XP (Speed)
- **Perfect:** +15 XP (Growth)
- **Too Hard:** +20 XP (Grit)

---
*Tip: Use `dojo hint` if you get stuck.*
    """
    console.print(Panel(Markdown(guide), title="Recommended Workflow", border_style="green"))
    Prompt.ask("Press Enter to return to menu")
    return 0


def run_onboarding(notes_root: Path) -> int:
    """
    Run the first-time setup wizard.
    """
    console.clear()
    console.print(Panel(
        "[bold gold1]INITIALIZING SYSTEM...[/bold gold1]\n\n"
        "Welcome to [bold white]NEXUS DOJO[/bold white].\n"
        "This is not just a tool. It is a simulation of your future job.\n"
        "We are here to build your muscle memory and engineering intuition.",
        title="👋 WELCOME",
        border_style="blue",
        padding=(1, 2)
    ))
    
    if not Confirm.ask("\nReady to configure your profile?"):
        console.print("[dim]Exiting... Come back when you are ready to train.[/dim]")
        return 0

    # 1. Profile Setup
    console.print("\n[bold cyan]Step 1: Identity[/bold cyan]")
    name = Prompt.ask("What should the system call you?", default="Engineer")
    
    # Save Settings
    settings = {"user_name": name}
    save_settings(notes_root, settings)
    
    # Initialize XP
    skills = {"python": 0, "cli": 0, "api": 0, "testing": 0, "mixed": 0}
    save_skills(notes_root, skills)
    
    console.print(f"\n[green]Identity confirmed: {name}. Access granted.[/green]")
    
    # 2. Workflow Intro
    console.print("\n[bold cyan]Step 2: The Protocol[/bold cyan]")
    console.print("Your goal is to reach [bold]Master[/bold] rank. To do that, you must train.")
    console.print("Here is the recommended workflow:\n")
    
    # Use a Grid for precise control instead of Markdown list
    wf_grid = Table.grid(padding=(0, 1))
    wf_grid.add_column(justify="right", style="cyan bold")
    wf_grid.add_column()
    
    wf_grid.add_row("1.", "⚡ [bold]Quick Train:[/bold] The AI picks a drill for your weakest skill.")
    wf_grid.add_row("2.", "📜 [bold]Mission:[/bold] Read `MISSION.md` (Your ticket).")
    wf_grid.add_row("3.", "👀 [bold]Watch:[/bold] Run `dojo watch` to auto-test your code.")
    wf_grid.add_row("4.", "⌨️ [bold]Code:[/bold] Solve the problem.")
    wf_grid.add_row("5.", "✅ [bold]Log:[/bold] Rate difficulty to gain XP.")
    
    console.print(wf_grid)
    
    Prompt.ask("\nPress Enter to enter the Dojo")
    
    # Redirect to main menu
    return handle_menu(argparse.Namespace())


def handle_init(args: argparse.Namespace) -> int:
    """
    Create a local workspace skeleton for knowledge artifacts.
    """
    workspace = Path(args.path).expanduser()
    if workspace.exists() and any(workspace.iterdir()) and not args.force:
        print(
            f"Workspace {workspace} is not empty. Use --force to reuse it.",
            file=sys.stderr,
        )
        return 1

    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / "knowledge_base").mkdir(exist_ok=True)
    (workspace / "scratchpad").mkdir(exist_ok=True)

    readme_path = workspace / "README.txt"
    if not readme_path.exists() or args.force:
        readme_path.write_text(
            "NexusDojo workspace\n"
            "- knowledge_base: store source documents for ingestion.\n"
            "- scratchpad: iterative notes, experiments, and prompts.\n"
        )

    print(f"Workspace ready at {workspace.resolve()}")
    return 0


def handle_prompt(args: argparse.Namespace) -> int:
    """
    Display a stored system prompt for reference.
    """
    prompt_path = Path(args.file)
    if not prompt_path.is_absolute():
        repo_root = Path(__file__).resolve().parents[2]
        prompt_path = (repo_root / prompt_path).resolve()

    if not prompt_path.exists():
        print(f"Prompt file not found: {prompt_path}", file=sys.stderr)
        return 1

    print(f"--- Prompt: {prompt_path} ---")
    print(prompt_path.read_text())
    return 0


def handle_api_dry_run(args: argparse.Namespace) -> int:
    """
    Build an API request payload using an environment variable for the key.
    """
    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        print(
            f"Missing API key: set {args.api_key_env}=<your key>",
            file=sys.stderr,
        )
        return 1

    # Construct a representative payload without sending it.
    payload = {
        "provider": args.provider,
        "model": args.model,
        "messages": [{"role": "user", "content": args.message}],
        "headers": {
            "Authorization": f"Bearer {api_key[:4]}...redacted",
        },
    }

    print("API dry run (no network call).")
    print("Payload:")
    for key, value in payload.items():
        print(f"- {key}: {value}")
    return 0





def handle_start(args: argparse.Namespace) -> int:
    """
    Create a kata from a template and stamp it with basic metadata.
    """
    idea = (args.idea or "").strip()
    kata_root = Path(args.root).expanduser()
    notes_root = Path(args.notes_root).expanduser()
    notes_root.mkdir(parents=True, exist_ok=True)

    stored_settings = load_settings(notes_root)
    pillar_hint = args.pillar or stored_settings.get("pillar")
    level_hint = args.level or stored_settings.get("level")
    mode_hint = args.mode or stored_settings.get("mode")
    tests_pref = args.tests or stored_settings.get("tests")
    scaffold_mode = args.scaffold
    offline_mode = bool(getattr(args, "offline", False))
    interactive = sys.stdin.isatty()

    prompt_user = (args.guided or not idea) and interactive
    if args.reuse_settings and not stored_settings and prompt_user:
        print("No saved settings found; switching to guided prompts.", file=sys.stderr)
        args.reuse_settings = False

    if prompt_user and not args.reuse_settings:
        pillar_hint = Prompt.ask(
            "Focus pillar (python/cli/api/testing/mixed)",
            default=pillar_hint or "mixed",
            choices=["python", "cli", "api", "testing", "mixed"],
        )
        mode_hint = Prompt.ask(
            "Mode/template (script/fastapi/rag/mcp)",
            default=mode_hint or "script",
            choices=["script", "fastapi", "rag", "mcp"],
        )
        level_hint = Prompt.ask(
            "Difficulty (foundation/proficient/stretch)",
            default=level_hint or "foundation",
            choices=["foundation", "proficient", "stretch"],
        )
        tests_pref = Prompt.ask(
            "Test scaffolding (edge/smoke/skip)",
            default=tests_pref or "edge",
            choices=["edge", "smoke", "skip"],
        )
        save_settings(
            notes_root,
            {
                "pillar": pillar_hint,
                "mode": mode_hint,
                "level": level_hint,
                "tests": tests_pref,
            },
        )

    console.print(
        f"Settings: [cyan]pillar={pillar_hint or 'mixed'}[/cyan]"
        f" [cyan]mode={mode_hint or 'script'}[/cyan]"
        f" [cyan]level={level_hint or 'foundation'}[/cyan]"
        f" [cyan]tests={tests_pref or ('edge' if prompt_user else 'smoke')}[/cyan]"
        f" [cyan]offline={'yes' if offline_mode else 'no'}[/cyan]"
    )
    resolved_template = resolve_template(args.template, mode_hint)
    if not idea:
        selected_idea: Optional[str] = None
        if prompt_user and not args.yes:
            if offline_mode:
                print("Offline mode: skipping model calls for ideas.", file=sys.stderr)
            with console.status("[bold green]Picking kata idea...[/bold green]", spinner="dots"):
                options, options_fallback = pick_idea_options(
                    provider=DEFAULT_IDEA_PROVIDER,
                    model=DEFAULT_IDEA_MODEL,
                    kata_root=kata_root,
                    notes_root=notes_root,
                    pillar_hint=pillar_hint,
                    level_hint=level_hint,
                    mode_hint=mode_hint,
                    max_options=3,
                    offline=offline_mode,
                )
            if options:
                console.print("Pick a kata:")
                for idx, opt in enumerate(options, start=1):
                    console.print(f"[cyan]{idx})[/cyan] {strip_idea_prefix(opt)}")
                console.print("[cyan]m)[/cyan] Manual idea")
                console.print("[cyan]c)[/cyan] Cancel")
                choice = Prompt.ask("Choose", default="1").strip().lower()
                if choice in {"c", "cancel"}:
                    console.print("Canceled.")
                    return 0
                if choice.startswith("m"):
                    manual = Prompt.ask("Enter your idea").strip()
                    if not manual:
                        console.print("No idea provided. Canceled.")
                        return 0
                    selected_idea = normalize_idea_line(manual)
                else:
                    try:
                        choice_idx = int(choice)
                    except ValueError:
                        choice_idx = 1
                    choice_idx = max(1, min(choice_idx, len(options)))
                    selected_idea = normalize_idea_line(options[choice_idx - 1])
                if options_fallback:
                    print("Note: LLM idea picker unavailable; used curated options.", file=sys.stderr)
        if not selected_idea:
            print("No idea provided; using adaptive idea picker...", file=sys.stderr)
            with console.status("[bold green]Generating idea...[/bold green]", spinner="dots"):
                picked, used_fallback = pick_idea_with_hints(
                    provider=DEFAULT_IDEA_PROVIDER,
                    model=DEFAULT_IDEA_MODEL,
                    kata_root=kata_root,
                    notes_root=notes_root,
                    pillar_hint=pillar_hint,
                    level_hint=level_hint,
                    mode_hint=mode_hint,
                    offline=offline_mode,
                )
            if not picked:
                print("Idea picker failed; using curated fallback.", file=sys.stderr)
                picked = fallback_idea(
                    pillar_hint=pillar_hint,
                    level_hint=level_hint,
                    mode_hint=mode_hint,
                )
            if not picked:
                print("Unable to generate an idea. Please provide one manually.", file=sys.stderr)
                return 1
            selected_idea = normalize_idea_line(picked)
            if used_fallback:
                print("Note: LLM idea picker unavailable; used curated fallback.", file=sys.stderr)
        idea = selected_idea

    idea_line = normalize_idea_line(idea)
    idea_title = strip_idea_prefix(idea_line)
    slug_base = slugify(idea_title)
    slug = slug_base
    if not slug:
        print("Idea is empty after slugifying; provide a short description.", file=sys.stderr)
        return 1

    kata_root.mkdir(parents=True, exist_ok=True)
    target_dir = kata_root / slug

    if target_dir.exists() and any(target_dir.iterdir()) and not args.force:
        alt_slug = next_available_slug(slug_base, kata_root)
        if not sys.stdin.isatty() or args.yes:
            console.print(f"[yellow]Kata directory {target_dir} exists; using alternate slug {alt_slug}.[/yellow]")
            slug = alt_slug
            target_dir = kata_root / slug
        else:
            console.print(f"Kata directory [cyan]{target_dir}[/cyan] exists and is not empty.")
            choice = Prompt.ask(f"Options: [r] reuse (force), [n] new slug {alt_slug} (default), [c] cancel", default="n").strip().lower()
            if choice.startswith("r"):
                args.force = True
            elif choice.startswith("c"):
                console.print("Canceled.")
                return 0
            else:
                slug = alt_slug
                target_dir = kata_root / slug
                console.print(f"Using alternate slug: [cyan]{slug}[/cyan]")

    template_dir = TEMPLATES_ROOT / resolved_template
    if not template_dir.exists():
        print(f"Template not found: {template_dir}", file=sys.stderr)
        return 1

    shutil.copytree(template_dir, target_dir, dirs_exist_ok=args.force)

    replacements = {
        "IDEA": idea_title,
        "SLUG": slug,
        "TEMPLATE": resolved_template,
        "CREATED_AT": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    apply_placeholders_tree(target_dir, replacements)

    scaffolded = False
    should_scaffold = (
        resolved_template in {"script", "fastapi"}
        and scaffold_mode in {"auto", "llm"}
        and (interactive or scaffold_mode == "llm")
    )
    fallback_used_scaffold = False
    if should_scaffold:
        spec, fallback_used_scaffold = generate_scaffold_spec(
            idea_line=idea_line,
            pillar_hint=pillar_hint,
            level_hint=level_hint,
            template=resolved_template,
            offline=offline_mode,
        )
        if spec:
            apply_kata_scaffold(target_dir, spec, template=resolved_template, overwrite_existing=True)
            scaffolded = True
    
    # Generate MISSION.md and test_mission.py
    mission_md_content, acceptance_criteria, fallback_used_mission = generate_mission_spec(
        project_dir=target_dir,
        idea_line=idea_line,
        pillar_hint=pillar_hint,
        level_hint=level_hint,
        template=resolved_template,
        notes_root=notes_root,
        offline=offline_mode,
    )
    console.print(f"Generated [green]MISSION.md[/green] and [green]test_mission.py[/green] for: [bold]{idea_title}[/bold]")
    if fallback_used_mission:
        print("Note: LLM unavailable for mission spec; using curated fallback.", file=sys.stderr)

    # Mission Injection Logic
    docstring_mission = "\n".join([line for line in mission_md_content.splitlines() if not line.startswith("# Mission")])
    mission_header = f'"""{idea_title}\n\nMISSION SPECS:\n{docstring_mission}\n"""\n'

    if not scaffolded:
        # Use smart boilerplate for RAG/MCP or failed scaffolds
        set_default_main_py_content(target_dir, resolved_template, idea_title, mission_md_content)
    else:
        # Prepend mission to existing scaffolded main.py
        main_py = target_dir / "main.py"
        if main_py.exists():
            original_content = main_py.read_text()
            # Remove any leading docstring to avoid double mission headers
            if original_content.startswith('"""'):
                end_idx = original_content.find('"""', 3)
                if end_idx != -1:
                    original_content = original_content[end_idx + 3 :].lstrip()
            
            main_py.write_text(mission_header + original_content)

    # Write metadata for progression tracking
    (target_dir / ".kata.json").write_text(json.dumps({
        "pillar": pillar_hint or "mixed",
        "level": level_hint or "foundation",
        "template": resolved_template,
        "created_at": datetime.now().isoformat()
    }, indent=2))

    effective_tests_pref = tests_pref or ("edge" if prompt_user else "smoke")
    if effective_tests_pref != "skip":
        seed_test_scaffold(target_dir, resolved_template, idea_line, include_edge=(effective_tests_pref == "edge"))

    # Show Tree
    tree = Tree(f"📂 [bold green]{target_dir.name}[/bold green]")
    tree.add("📜 MISSION.md")
    tree.add("🐍 main.py")
    tests_node = tree.add("📂 tests")
    tests_node.add("🐍 __init__.py")
    if effective_tests_pref != "skip":
        tests_node.add("🐍 test_smoke.py")
        if effective_tests_pref == "edge":
            tests_node.add("🐍 test_edge_cases.py")
    
    console.print(Panel(tree, title="Scaffold Generated", border_style="green"))
    mission_preview_path = target_dir / "MISSION.md"
    if mission_preview_path.exists():
        console.print("[bold]MISSION.md[/bold]")
        type_out_text("\n".join(mission_preview_path.read_text().splitlines()[:10]))
        console.print()

    console.print(f"Created kata at [green]{target_dir}[/green]")
    if scaffolded:
        console.print("[green]Scaffolded: kata.md, stubs, and focused tests generated.[/green]")
        if fallback_used_scaffold:
            print("Note: LLM scaffold unavailable; used deterministic fallback.", file=sys.stderr)
    if effective_tests_pref != "skip":
        console.print("[green]Tests seeded: Run `dojo check` to verify.[/green]")
    
    # --- Zero-Friction Launch ---
    # If this was a Quick Train (yes=True) or user confirms, we launch.
    should_launch = args.yes # Auto-launch for Quick Train
    if not should_launch and interactive:
        should_launch = Confirm.ask("🚀 Launch Training Environment now?", default=True)

    if should_launch:
        launch_session(target_dir)
        return 0 # launch_session might replace process, but if not, we return success.

    console.print(
        "[bold blue]Next steps:[/bold blue]\n"
        f"- [bold]cd {target_dir.name}[/bold]\n"
        "- Read [green]MISSION.md[/green] for your task.\n"
        "- Code your solution in [green]main.py[/green].\n"
        "- Run [bold yellow]dojo check[/bold yellow] to get instant feedback from your Sensei."
    )
    return 0


def launch_session(project_dir: Path) -> None:
    """
    Launch the editor and watch mode. Detects tmux for split-pane glory.
    """
    import subprocess
    import os
    
    # Check for TMUX
    in_tmux = os.environ.get("TMUX") is not None
    
    if in_tmux:
        console.print("[green]Tmux detected. Configuring split-pane environment...[/green]")
        
        # Build the command for the new pane (dojo watch)
        watch_cmd_parts = [
            sys.executable, "-m", "nexusdojo.cli", "watch",
            project_dir.name,
            "--root", str(project_dir.parent),
            "--notes-root", str(DEFAULT_NOTES_ROOT),
        ]

        watch_cmd_str = " ".join(shlex.quote(part) for part in watch_cmd_parts)
        watch_cmd_str += "; rc=$?; echo \"[watch pane exited code ${rc}]\"; read -r _"

        # 1. Split window horizontally, cd to project, run dojo watch
        split_result = subprocess.run([
            "tmux", "split-window", "-h", 
            "-c", str(project_dir), 
            watch_cmd_str
        ], capture_output=True, text=True)
        if split_result.returncode != 0:
            console.print("[red]Tmux split failed; watch pane not started.[/red]")
            if split_result.stderr:
                console.print(f"[dim]{summarize_failure_output(split_result.stderr)}[/dim]")
            console.print(f"[yellow]Run manually:[/yellow] {watch_cmd_str}")
        
        # 2. Open nvim in the current pane
        # We replace the current process with nvim to keep the flow clean
        console.print("[dim]Launching Neovim...[/dim]")
        
        # We need to change cwd for the nvim process
        os.chdir(project_dir)
        
        # Use execvp to replace the python process with nvim
        # We open MISSION.md (read-only reference) and main.py (to edit)
        os.execvp("nvim", ["nvim", "main.py", "MISSION.md"])
        
    else:
        console.print("[yellow]Tip: Run 'dojo menu' inside tmux for auto-split 'Watch Mode'.[/yellow]")
        console.print("[dim]Launching Neovim...[/dim]")
        os.chdir(project_dir)
        subprocess.run(["nvim", "main.py", "MISSION.md"])


def set_default_main_py_content(target_dir: Path, template: str, idea_title: str, mission_content: str = "") -> None:
    """
    Sets a default main.py content with Mission Injection and Smart Imports.
    """
    main_py_path = target_dir / "main.py"
    
    # Smart Imports
    imports = []
    if "json" in mission_content.lower(): imports.append("import json")
    if "csv" in mission_content.lower(): imports.append("import csv")
    if "regex" in mission_content.lower() or "pattern" in mission_content.lower(): imports.append("import re")
    if "file" in mission_content.lower() or "path" in mission_content.lower(): imports.append("from pathlib import Path")
    if "async" in mission_content.lower(): imports.append("import asyncio")
    if "env" in mission_content.lower(): imports.append("import os")
    
    import_block = "\n".join(imports)
    
    # Clean mission content for docstring (remove header to save space)
    docstring_mission = "\n".join([line for line in mission_content.splitlines() if not line.startswith("# Mission")])

    if template == "rag":
        content = f'''"""RAG Kata: {idea_title}

MISSION SPECS:
{docstring_mission}
"""
from typing import List, Dict
{import_block}

def retrieve_context(query: str, top_k: int = 3) -> List[str]:
    """
    Simulates retrieving relevant text chunks from a vector database.
    Implement your RAG logic here (e.g., using ChromaDB, FAISS).
    """
    # TODO: Implement actual RAG retrieval
    return [f"Context for '{{query}}' chunk {{i+1}}" for i in range(top_k)]

def generate_response(query: str, context: List[str]) -> str:
    """
    Simulates generating a response using an LLM based on query and context.
    """
    # TODO: Implement LLM call with RAG context
    return f"Response to '{{query}}' based on context: {{context}}"

def main():
    print("RAG Pipeline Kata: Implement retrieve_context and generate_response.")
    print("Run tests in the 'tests' folder.")

if __name__ == "__main__":
    main()
'''
    elif template == "mcp":
        content = f'''"""MCP Server Kata: {idea_title}

MISSION SPECS:
{docstring_mission}
"""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any
{import_block}

app = FastAPI(title="Micro-Capability Protocol Server")

class ToolRequest(BaseModel):
    tool_name: str
    tool_args: Dict[str, Any]

@app.get("/health")
async def health():
    return {{"status": "ok"}}

@app.post("/execute_tool")
async def execute_tool(request: ToolRequest):
    """
    Executes a specific tool/capability based on the request.
    TODO: Implement your tools here (e.g., search, calculator, data lookup).
    """
    if request.tool_name == "example_tool":
        # Example tool implementation
        result = {{"message": f"Executed {{request.tool_name}} with args: {{request.tool_args}}"}}
        return result
    else:
        return {{"error": f"Tool '{{request.tool_name}}' not found."}}

def main():
    print("MCP Server Kata: Implement and expose micro-capabilities via HTTP.")
    print("Run tests in the 'tests' folder, then `uvicorn main:app --reload`.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
'''
    else:
        content = f'''"""Kata: {idea_title}

MISSION SPECS:
{docstring_mission}
"""
{import_block}

def main():
    print("Implement your kata logic here.")
    # Refer to the Mission Specs above for requirements.

if __name__ == "__main__":
    main()
'''
    main_py_path.write_text(content)


def handle_play(args: argparse.Namespace) -> int:
    """
    Create a temporary playground environment.
    """
    # Create scratchpad directory
    scratch_root = Path(DEFAULT_WORKSPACE) / "scratchpad"
    scratch_root.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    play_dir = scratch_root / f"playground_{timestamp}"
    play_dir.mkdir()
    
    # Init simple environment
    (play_dir / "main.py").write_text('"""NexusDojo Playground"""\n\ndef main():\n    print("Experimental mode.")\n\nif __name__ == "__main__":\n    main()\n')
    (play_dir / "README.md").write_text("# Playground\n\nTransient environment. Deletes on cleanup.")
    
    console.print(f"[green]Opened playground at {play_dir.name}[/green]")
    launch_session(play_dir)
    
    # Cleanup prompt after session ends
    if Confirm.ask("Delete this playground session?"):
        shutil.rmtree(play_dir)
        console.print("Playground deleted.")
    
    return 0


def handle_solve(args: argparse.Namespace) -> int:
    """
    Generate a solution for the current kata using the AI.
    """
    kata_root = Path(args.root or DEFAULT_KATA_ROOT).expanduser()
    if args.project:
        project_dir = kata_root / args.project
    else:
        project_dir = Path.cwd()

    if not (project_dir / "MISSION.md").exists():
        console.print("[red]Not a valid kata directory (missing MISSION.md).[/red]")
        return 1

    if not Confirm.ask("[bold red]WARNING:[/bold red] Using 'solve' forfeits XP for this kata. Continue?"):
        return 0

    console.print("[yellow]Consulting the Archives...[/yellow]")
    
    mission = (project_dir / "MISSION.md").read_text()
    current_code = (project_dir / "main.py").read_text()
    
    system = "You are a Python Expert. Provide a complete, working solution for the given Mission. Output ONLY code."
    user = f"Mission:\n{mission}\n\nCurrent Stub:\n{current_code}\n\nProvide the full solution for main.py."
    
    solution_code = call_idea_api(DEFAULT_IDEA_PROVIDER, DEFAULT_IDEA_MODEL, [{"role": "system", "content": system}, {"role": "user", "content": user}])
    
    if solution_code:
        # Strip markdown fences if present
        solution_code = solution_code.replace("```python", "").replace("```", "")
        (project_dir / "solution.py").write_text(solution_code)
        console.print(f"[green]Solution written to {project_dir / 'solution.py'}.[/green]")
        
        # Mark as cheated
        meta_path = project_dir / ".kata.json"
        if meta_path.exists():
            meta = json.loads(meta_path.read_text())
            meta["cheated"] = True
            meta_path.write_text(json.dumps(meta, indent=2))
    else:
        console.print("[red]Failed to generate solution.[/red]")
        
    return 0


def handle_reset(args: argparse.Namespace) -> int:
    """
    Reset the kata to its initial state.
    """
    kata_root = Path(args.root or DEFAULT_KATA_ROOT).expanduser()
    if args.project:
        project_dir = kata_root / args.project
    else:
        project_dir = Path.cwd()

    meta_path = project_dir / ".kata.json"
    if not meta_path.exists():
        console.print("[red]Cannot reset: missing .kata.json metadata.[/red]")
        return 1

    if not Confirm.ask("Reset main.py to boilerplate? This deletes your code."):
        return 0

    meta = json.loads(meta_path.read_text())
    template = meta.get("template", "script")
    
    # Re-read Mission for injection
    mission_content = ""
    if (project_dir / "MISSION.md").exists():
        mission_content = (project_dir / "MISSION.md").read_text()

    # Determine title
    readme = project_dir / "README.md"
    title = "Kata"
    if readme.exists():
        title = readme.read_text().splitlines()[0].replace("#", "").strip()

    set_default_main_py_content(project_dir, template, title, mission_content)
    console.print("[green]Reset complete.[/green]")
    return 0


def install_dependencies(project_dir: Path) -> None:
    """
    Check for requirements.txt and install missing dependencies.
    """
    req_path = project_dir / "requirements.txt"
    if not req_path.exists():
        return

    # Check if packages are installed (lazy check via pip freeze? Too slow).
    # Better: Just run pip install if user approves.
    # To reduce friction: Check if we are in venv.
    
    # Simplified Logic:
    # 1. Read requirements.
    # 2. If non-empty, ask to install.
    reqs = req_path.read_text().strip()
    if not reqs:
        return

    # We only prompt if we suspect they aren't installed? 
    # Or we just do it silently/quickly if we are in the 'dojo check' flow?
    # Let's prompt ONCE per session ideally, but for now, prompt if missing.
    # Actually, let's just use pip install -r ... it's fast if already satisfied.
    
    # Only run if we haven't checked recently? 
    # Let's add a marker file .deps_installed to avoid constant pip calls
    if (project_dir / ".deps_installed").exists():
        # Check timestamp? Nah, simple is better.
        return

    console.print("[yellow]Dependencies detected. Installing...[/yellow]")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req_path)], check=True, capture_output=True)
        (project_dir / ".deps_installed").touch()
        console.print("[green]Dependencies installed.[/green]")
    except subprocess.CalledProcessError as exc:
        console.print("[red]Failed to install dependencies.[/red]")
        stderr = (exc.stderr or "").strip()
        if stderr:
            console.print(f"[dim]{summarize_failure_output(stderr)}[/dim]")
        console.print(f"[yellow]Try manually running:[/yellow] {sys.executable} -m pip install -r {req_path}")


def handle_log(args: argparse.Namespace) -> int:
    """
    Append a log entry to the kata log and central notes log.
    """
    kata_root = Path(args.root).expanduser()
    notes_root = Path(args.notes_root).expanduser()
    notes_root.mkdir(parents=True, exist_ok=True)

    project_dir = kata_root / args.project
    if not project_dir.exists():
        print(f"Kata not found at {project_dir}", file=sys.stderr)
        return 1

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"- [{timestamp}] {args.note}\n"

    project_log = project_dir / "LOG.md"
    project_log.parent.mkdir(parents=True, exist_ok=True)
    append_line(project_log, entry)

    central_log = notes_root / "log.md"
    append_line(central_log, f"- [{timestamp}] {args.project}: {args.note}\n")

    print(f"Logged entry to {project_log} and {central_log}")
    return 0


def handle_brief(args: argparse.Namespace) -> int:
    """
    Generate a simple brief from recent log entries.
    """
    kata_root = Path(args.root).expanduser()
    notes_root = Path(args.notes_root).expanduser()
    notes_root.mkdir(parents=True, exist_ok=True)
    briefs_dir = notes_root / "briefs"
    briefs_dir.mkdir(parents=True, exist_ok=True)

    if args.since:
        try:
            since_dt = datetime.strptime(args.since, "%Y-%m-%d")
        except ValueError:
            print("Invalid --since format. Use YYYY-MM-DD.", file=sys.stderr)
            return 1
    else:
        since_dt = datetime.now() - timedelta(days=7)

    entries = collect_entries(kata_root, notes_root, since_dt)
    if not entries:
        print("No entries found for the requested window.")
        return 0

    today_str = datetime.now().strftime("%Y-%m-%d")
    brief_path = briefs_dir / f"{today_str}.md"
    content_lines = [
        f"# NexusDojo Brief ({today_str})",
        f"Since: {since_dt.strftime('%Y-%m-%d')}",
        "",
    ]
    for project, ts, note in entries:
        content_lines.append(f"- [{ts}] {project}: {note}")

    brief_path.write_text("\n".join(content_lines))
    print(brief_path.read_text())
    print(f"\nBrief saved to {brief_path}")
    return 0


def handle_calibrate(args: argparse.Namespace) -> int:
    """
    Record a quick self-assessment for a pillar.
    """
    notes_root = Path(args.notes_root).expanduser()
    notes_root.mkdir(parents=True, exist_ok=True)
    calibration_path = notes_root / "calibrations.md"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = (
        f"- [{timestamp}] pillar={args.pillar} score={args.score}"
        f"{' note=' + args.note if args.note else ''}\n"
    )
    append_line(calibration_path, entry)
    print(f"Logged calibration to {calibration_path}")
    return 0


def handle_dashboard(args: argparse.Namespace) -> int:
    """
    Show a compact dashboard with practice signals and hints.
    """
    kata_root = Path(args.root).expanduser()
    notes_root = Path(args.notes_root).expanduser()

    katas = list_katas(kata_root)
    completed_drills = count_completed_drills(kata_root, notes_root)
    recent = latest_activity(kata_root, notes_root)
    calib_path = notes_root / "calibrations.md"
    scores = parse_calibrations(calib_path) if calib_path.exists() else {}
    trend = calibration_trend(calib_path) if calib_path.exists() else {}
    weakest = weakest_pillar(scores)
    suggestion = fallback_idea(pillar_hint=weakest, level_hint="foundation", mode_hint=None)
    settings = load_settings(notes_root)
    balance = practice_balance(scores)

    print("NexusDojo dashboard")
    print(f"- Katas: {len(katas)} ({', '.join(katas[-3:]) or 'none'})")
    print(f"- Completed drills (with history): {completed_drills}")
    print(f"- Weakest pillar: {weakest or 'unknown'} | Trend: {trend or 'no history'}")
    print(f"- Practice balance: {balance or 'log a calibration to start'}")
    if recent:
        project, ts, note = recent
        print(f"- Continue: {project} (last at {ts}) -> {note}")
    else:
        print("- Continue: none yet, start a kata to unlock suggestions.")
    if suggestion:
        print(f"- Suggested next kata: {suggestion}")
    if settings:
        print(f"- Last guided defaults: pillar={settings.get('pillar')} mode={settings.get('mode')} level={settings.get('level')} tests={settings.get('tests')}")
    print(f"- Idea picker defaults: provider={DEFAULT_IDEA_PROVIDER}, model={DEFAULT_IDEA_MODEL}")
    return 0


def handle_history(args: argparse.Namespace) -> int:
    """
    Display recent log activity and practice stats.
    """
    kata_root = Path(args.root).expanduser()
    notes_root = Path(args.notes_root).expanduser()
    notes_root.mkdir(parents=True, exist_ok=True)
    active_profile = ensure_profile_selected(notes_root)
    settings = load_settings(notes_root)
    user_name = settings.get("user_name", active_profile or "Engineer")

    window_days = max(1, getattr(args, "days", 30))
    since_dt = datetime.now() - timedelta(days=window_days)
    recent_entries = collect_entries(kata_root, notes_root, since_dt)
    all_entries = collect_entries(kata_root, notes_root, datetime.min)
    completed_drills = count_completed_drills(kata_root, notes_root)
    streak = get_streak_heatmap(notes_root, days=7)
    last_entry = all_entries[-1] if all_entries else None

    stats = Table(box=box.MINIMAL_DOUBLE_HEAD)
    stats.add_column("Metric", style="cyan")
    stats.add_column("Value", style="white")
    stats.add_row("Completed katas", str(completed_drills))
    stats.add_row("Log entries", str(len(all_entries)))
    stats.add_row("7d streak", streak)
    if last_entry:
        stats.add_row("Last entry", f"{last_entry[1]} — {last_entry[0]}")
    else:
        stats.add_row("Last entry", "No history yet")

    console.print(Panel(stats, title=f"📊 Profile & History ({user_name})", border_style="cyan"))

    activity = Table(title=f"Recent activity (last {window_days} days)", box=box.MINIMAL)
    activity.add_column("When", style="cyan", no_wrap=True)
    activity.add_column("Project", style="green", no_wrap=True)
    activity.add_column("Note", style="white")
    if recent_entries:
        for project, ts, note in recent_entries[-10:]:
            activity.add_row(ts, project or "central", summarize_text(note, 80))
    else:
        activity.add_row("-", "-", "No entries yet. Finish a kata and log a note to populate this.")
    console.print(activity)
    console.print()

    # Profile actions submenu
    console.print("[bold]Profile actions:[/bold]")
    console.print(" [bold cyan]1[/bold cyan] View profile details")
    console.print(" [bold cyan]2[/bold cyan] Create new profile")
    console.print(" [bold cyan]3[/bold cyan] Switch profile")
    console.print(" [bold cyan]4[/bold cyan] Log out / landing state\n")
    choice = Prompt.ask(
        "[italic grey50]Select an option [1-4]:[/italic grey50]",
        choices=["1", "2", "3", "4", ""],
        default="1",
        show_choices=False,
    ) or "1"

    if choice == "2":
        name = sanitize_profile_name(Prompt.ask("Enter a profile name", default="engineer"))
        if not name:
            name = "engineer"
        set_current_profile_name(notes_root, name)
        save_settings(notes_root, {"user_name": name})
        console.print(f"[green]Profile '{name}' created and set active.[/green]")
        Prompt.ask("\nPress Enter to return to menu")
    elif choice == "3":
        profiles = list_profiles(notes_root)
        if not profiles:
            console.print("[yellow]No profiles to switch to. Create one first.[/yellow]")
            Prompt.ask("\nPress Enter to return to menu")
        else:
            target = Prompt.ask("Choose profile", choices=profiles, default=profiles[0])
            set_current_profile_name(notes_root, target)
            console.print(f"[green]Switched to profile '{target}'.[/green]")
            Prompt.ask("\nPress Enter to return to menu")
    elif choice == "4":
        clear_current_profile(notes_root)
        console.print("[dim]Logged out. You'll be asked to choose a profile next time.[/dim]")
        Prompt.ask("\nPress Enter to return to menu")
    else:
        # View only, already shown
        Prompt.ask("\nPress Enter to return to menu")
    return 0


def handle_continue(args: argparse.Namespace) -> int:
    """
    Show the most recent kata and where to resume.
    """
    kata_root = Path(args.root).expanduser()
    notes_root = Path(args.notes_root).expanduser()
    recent = latest_activity(kata_root, notes_root)
    if not recent:
        print("No activity found yet. Start a kata with `dojo start`.", file=sys.stderr)
        return 1
    project, ts, note = recent
    project_dir = kata_root / project
    readme = project_dir / "README.md"
    if readme.exists():
        lines = readme.read_text().splitlines()
        brief = lines[0] if lines else "README is empty."
        brief = brief.lstrip("# ").strip() or brief
    else:
        brief = "README not found yet."
    print("Resume kata")
    print(f"- Project: {project}")
    print(f"- Last activity: {ts} -> {note}")
    print(f"- Path: {project_dir.resolve()}")
    print(f"- Brief: {brief}")
    log_hint = project_dir / "LOG.md"
    print(f"- Next: open code, run tests (`python -m unittest`), then `dojo log {project} --note \"...\"`.")
    if log_hint.exists():
        last_log = last_lines(log_hint, 3)
        if last_log:
            print(f"- Recent log lines:\n{last_log}")
    return 0


def handle_transcript(args: argparse.Namespace) -> int:
    """
    Append a manual transcript entry, optionally with a lightweight summary.
    """
    notes_root = Path(args.notes_root).expanduser()
    notes_root.mkdir(parents=True, exist_ok=True)
    transcript_path = notes_root / "transcript.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [f"- [{timestamp}] {args.text}"]
    if args.summarize:
        lines.append(f"  Summary: {summarize_text(args.text)}")
    append_line(transcript_path, "\n".join(lines) + "\n")
    print(f"Transcript updated: {transcript_path}")
    return 0


def handle_hint(args: argparse.Namespace) -> int:
    """
    Pull a concise hint for a kata with rate limiting and fallbacks.
    """
    kata_root = Path(args.root).expanduser()
    notes_root = Path(args.notes_root).expanduser()
    project_dir = kata_root / args.project
    if not project_dir.exists():
        print(f"Kata not found at {project_dir}", file=sys.stderr)
        return 1

    allowed, wait_msg, remaining = check_hint_rate_limit(args.project, notes_root)
    if not allowed:
        print(wait_msg, file=sys.stderr)
        return 1

    messages = build_hint_prompt(project_dir, notes_root, args.question)
    if args.dry_run:
        print("System prompt:")
        print(messages[0]["content"])
        print("\nUser prompt:")
        print(messages[1]["content"])
        return 0

    hint = None
    if not args.offline:
        hint = call_idea_api(
            provider=args.provider,
            model=args.model,
            messages=messages,
        )
    fallback_used = False
    if not hint:
        hint = fallback_hint(args.question)
        fallback_used = True
        print("Model unavailable; using curated fallback.", file=sys.stderr)

    record_hint_use(args.project, notes_root)
    label = "Hint"
    if args.offline or fallback_used:
        label += " [offline fallback]"
    quota_line = f"(remaining today: {remaining})" if remaining is not None else ""
    
    console.print(Panel(
        Markdown(hint),
        title=f"💡 {label} {quota_line}",
        border_style="yellow"
    ))
    return 0


def handle_test_hints(args: argparse.Namespace) -> int:
    """
    Generate edge-case test TODOs (skipped) for a kata.
    """
    kata_root = Path(args.root).expanduser()
    notes_root = Path(args.notes_root).expanduser()
    project_dir = kata_root / args.project
    if not project_dir.exists():
        print(f"Kata not found at {project_dir}", file=sys.stderr)
        return 1

    messages = build_test_hint_prompt(project_dir, notes_root, args.max)
    if args.dry_run:
        print("System prompt:")
        print(messages[0]["content"])
        print("\nUser prompt:")
        print(messages[1]["content"])
        return 0

    content = None
    if not args.offline:
        content = call_idea_api(
            provider=args.provider,
            model=args.model,
            messages=messages,
        )
    fallback_used = args.offline
    hints = parse_bullet_list(content) if content else None
    if not hints:
        hints = fallback_edge_hints(project_dir)
        fallback_used = True
        print("Model unavailable; using curated edge-case hints.", file=sys.stderr)
    if args.max and len(hints) > args.max:
        hints = hints[: args.max]

    write_edge_hint_tests(project_dir, hints)
    label = "Edge-case TODOs"
    if fallback_used:
        label += " [offline fallback]"
    print(f"{label} written to {project_dir / 'tests' / 'test_edge_hints.py'}")
    return 0


def get_streak_heatmap(notes_root: Path, days: int = 7) -> str:
    """
    Generate a simple ASCII heatmap of recent activity.
    """
    log_path = notes_root / "log.md"
    active_dates = set()
    if log_path.exists():
        for line in log_path.read_text().splitlines():
            # Minimal parsing for speed
            if line.startswith("- ["):
                try:
                    date_str = line[3:13] # YYYY-MM-DD
                    active_dates.add(date_str)
                except: pass
    
    heatmap = []
    today = datetime.now().date()
    for i in range(days - 1, -1, -1):
        d = today - timedelta(days=i)
        d_str = d.strftime("%Y-%m-%d")
        if d_str in active_dates:
            heatmap.append("[green]■[/green]")
        else:
            heatmap.append("[dim]□[/dim]")
            
    return " ".join(heatmap)


def find_active_kata_dir(cwd: Path) -> Optional[Path]:
    """
    Check if cwd or parents is a kata directory (has .kata.json or MISSION.md).
    """
    # Check current first
    if (cwd / ".kata.json").exists() or (cwd / "MISSION.md").exists():
        return cwd
    # Check parents until we hit a known root or too far
    for parent in cwd.parents:
        if (parent / ".kata.json").exists():
            return parent
        if parent.name == "dojo" and (parent / cwd.name).exists():
             # If we are in dojo/kata-name/subdir
             return parent / cwd.name
    return None

def format_pillar_label(pillar: str) -> str:
    return pillar.title()

def count_completed_drills(kata_root: Path, notes_root: Path) -> int:
    # Estimate based on unique projects in log or folders in dojo
    # Log is better for completed
    entries = collect_entries(kata_root, notes_root, datetime.min)
    unique_projects = {e[0] for e in entries}
    return len(unique_projects)

def resolve_last_kata(kata_root: Path, notes_root: Path) -> tuple[Optional[str], Optional[Path]]:
    recent = latest_activity(kata_root, notes_root)
    if not recent:
        # Fallback to finding newest directory in kata_root
        newest_project: Optional[str] = None
        newest_path: Optional[Path] = None
        newest_ts: Optional[datetime] = None
        if kata_root.exists():
            for project_dir in kata_root.iterdir():
                if not project_dir.is_dir():
                    continue
                meta_ts: Optional[datetime] = None
                meta_path = project_dir / ".kata.json"
                if meta_path.exists():
                    try:
                        meta = json.loads(meta_path.read_text())
                        meta_ts = datetime.fromisoformat(meta.get("created_at", ""))
                    except Exception:
                        meta_ts = None
                if meta_ts is None:
                    meta_ts = datetime.fromtimestamp(project_dir.stat().st_mtime)
                if newest_ts is None or meta_ts > newest_ts:
                    newest_ts = meta_ts
                    newest_project = project_dir.name
                    newest_path = project_dir
        return newest_project, newest_path
    project = recent[0]
    target_dir = kata_root / project
    return project, target_dir if target_dir.exists() else None

def peek_kata_summary(kata_dir: Path, notes_root: Path) -> None:
    # 1. File Tree
    tree = Tree(f"📂 [bold cyan]{kata_dir.name}[/bold cyan]")
    for path in sorted(kata_dir.rglob("*")):
        if path.name.startswith("."): continue
        if path.is_dir():
            # Simply showing top level structure for clarity
            continue 
        
        # relative path
        rel = path.relative_to(kata_dir)
        # Add to tree (simplified flat add for now, or recursive if we want)
        # Let's keep it simple: just show direct children and tests
        if len(rel.parts) > 2: continue # Don't go too deep
        
        icon = "📄"
        if path.suffix == ".py": icon = "🐍"
        if path.name == "MISSION.md": icon = "📜"
        if path.name == "README.md": icon = "📖"
        
        tree.add(f"{icon} {rel}")

    # 2. Content Preview
    readme = kata_dir / "README.md"
    mission = kata_dir / "MISSION.md"
    
    content_render = None
    if mission.exists():
        content_render = Markdown(mission.read_text())
        title = "MISSION.md"
    elif readme.exists():
        content_render = Markdown(readme.read_text())
        title = "README.md"
    else:
        content_render = Text("No documentation found.", style="italic dim")
        title = "Info"

    # Layout
    console.print(Panel(tree, title="Architecture", border_style="blue"))
    console.print(Panel(content_render, title=f"Preview: {title}", border_style="cyan"))

def quick_check_preview(kata_dir: Path, notes_root: Path) -> tuple[bool, str]:
    import subprocess
    if not (kata_dir / "tests").exists():
        return False, "No tests found."
    
    try:
        # Run tests silently
        result = subprocess.run(
            [sys.executable, "-m", "unittest"],
            cwd=kata_dir,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return True, "All tests passed."
        else:
            # Count failures
            count = result.stderr.count("FAIL") + result.stderr.count("ERROR")
            return False, f"Tests failed ({count} errors/failures)."
    except subprocess.TimeoutExpired:
        return False, "Tests timed out."
    except Exception as e:
        return False, f"Error running tests: {e}"



def render_progress_bar(current: int, total: int, width: int = 20) -> str:
    """
    Renders a static progress bar string.
    """
    if total == 0: total = 100 # Avoid div by zero
    percent = min(1.0, current / total)
    filled = int(width * percent)
    empty = width - filled
    
    # Color grading based on percentage
    color = "red"
    if percent > 0.33: color = "yellow"
    if percent > 0.66: color = "green"
    if percent >= 1.0: color = "cyan"
    
    bar = f"[{color}]{'━' * filled}[/{color}]{'[dim]━[/dim]' * empty}"
    return bar

def get_next_level_threshold(xp: int) -> int:
    # Matches get_level_info logic
    if xp < 100: return 100
    if xp < 300: return 300
    if xp < 600: return 600
    if xp < 1000: return 1000
    return 9999


def type_out_text(text: str, delay: float = 0.01) -> None:
    """
    Render text with a lightweight typing effect (line-paced).
    """
    for line in text.splitlines():
        console.print(line)
        pause = min(0.05, delay * max(1, len(line) / 6))
        time.sleep(pause)


def start_matrix_rain(pillar: str, mode: str, duration: float = 1.6) -> tuple[threading.Event, threading.Thread]:
    """
    Stream faint debug-style lines while an AI task runs.
    """
    stop_event = threading.Event()
    debug_templates = [
        "> [DEBUG] weakest='{pillar}' variance={var:.2f}",
        "> [TRACE] template='{mode}' noise={noise:.2f}",
        "> [DEBUG] scoring rubric: fluency={score:.2f}",
        "> [SYS] hint_sampler={hint:.2f} beam={beam}",
        "> [DEBUG] mission synth pass={pass_no}",
        "> [ANALYZE] context tokens={tokens}",
    ]
    def worker() -> None:
        start_time = time.time()
        lines = 0
        while not stop_event.is_set() and time.time() - start_time < duration and lines < 18:
            template = random.choice(debug_templates)
            line = template.format(
                pillar=pillar,
                mode=mode,
                var=random.random(),
                noise=random.random(),
                score=random.uniform(0.2, 0.95),
                hint=random.uniform(0.1, 0.9),
                beam=random.randint(2, 6),
                pass_no=random.randint(1, 3),
                tokens=random.randint(240, 1480),
            )
            console.print(f"[dim]{line}[/dim]")
            lines += 1
            time.sleep(0.12)
    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    return stop_event, thread


def stop_matrix_rain(stop_event: threading.Event, thread: threading.Thread) -> None:
    """
    Halt the matrix rain helper.
    """
    stop_event.set()
    thread.join(timeout=0.3)


def run_boot_diagnostics(kata_root: Path, notes_root: Path) -> None:
    """
    Show a short boot-up diagnostic before the menu renders.
    """
    steps = [
        ("CONNECTING", "Verifying local environment...", "OK"),
        ("NETWORK", f"Ollama ({DEFAULT_IDEA_MODEL})...", "LATENCY 4ms"),
        ("PROFILE", f"Loading {notes_root.name or 'profile'}...", "LOADED"),
        ("SYSTEM", f"Mounting workspace at {kata_root.name}...", "OK"),
    ]
    console.clear()
    for label, message, status in steps:
        console.print(f"[dim][ {label:^10} ][/dim] {message} [green]{status}[/green]")
        time.sleep(0.18)
    time.sleep(0.2)
    console.clear()


def handle_menu(_: argparse.Namespace) -> int:
    """
    Interactive menu for common tasks (Rich UI).
    """
    kata_root = Path(DEFAULT_KATA_ROOT)
    notes_root = Path(DEFAULT_NOTES_ROOT)
    notes_root.mkdir(parents=True, exist_ok=True) 
    
    if not (notes_root / "skills.json").exists():
        return run_onboarding(notes_root)

    force_lobby_view = False
    run_boot_diagnostics(kata_root, notes_root)

    # Require an active profile before continuing
    ensure_profile_selected(notes_root)

    # First-time tutorial flow (after profile selection)
    if is_first_time_user(kata_root, notes_root):
        tutorial_dir = ensure_tutorial_kata(kata_root)
        console.print("[dim]Launching tutorial...[/dim]")
        launch_session(tutorial_dir)
        return 0

    while True:
        import time # Import time locally here
        try:
            console.clear()
            # Gather context refresh on every loop
            active_kata_dir = find_active_kata_dir(Path.cwd())
            in_kata_context = active_kata_dir is not None and not force_lobby_view

            skills = load_skills(notes_root)
            settings = load_settings(notes_root)
            user_name = settings.get("user_name", "Engineer")
            recent_entries = collect_entries(kata_root, notes_root, datetime.min)
            
            valid_skills = {k: v for k, v in skills.items() if k != "mixed"}
            
            # Calculate derived stats
            total_xp = sum(v for k, v in valid_skills.items())
            completed_drills = count_completed_drills(kata_root, notes_root)
            heatmap = get_streak_heatmap(notes_root, days=7)
            
            # Determine highest and weakest pillar for Focus Highlight
            if valid_skills:
                strongest_pillar = max(valid_skills, key=valid_skills.get)
                weakest_pillar = min(valid_skills, key=valid_skills.get)
            else: # Default for brand new users
                strongest_pillar = "python"
                weakest_pillar = "python"
            
            strongest_level, _ = get_level_info(skills.get(strongest_pillar, 0))
            weakest_level, _ = get_level_info(skills.get(weakest_pillar, 0))


            # --- Dashboard Layout (Focus Highlight) ---
            
            top_grid = Table.grid(expand=True, padding=(0, 2))
            top_grid.add_column(ratio=3) # Left: User Info, Focus
            top_grid.add_column(ratio=2) # Right: Context, Logs, Skills
            
            # Left Side: User Info, XP, Katas, Streak, Skills
            left = Table.grid(padding=0)
            left.add_row(f"[bold gold1]USER:[/bold gold1] {user_name}")
            left.add_row(f"[bold]Completed Katas:[/bold] {completed_drills}")
            left.add_row(f"[bold]Total XP:[/bold] {total_xp}")
            left.add_row("")
            left.add_row("[bold]SKILL LEVELS:[/bold]")
            for pillar, xp in skills.items():
                if pillar == "mixed": continue
                level_title, progress = get_level_info(xp)
                left.add_row(f"• {format_pillar_label(pillar)}: [white]{level_title}[/white] ([dim]{progress}[/dim])")
            left.add_row("")
            left.add_row(f"[bold]STREAK:[/bold] {heatmap}")
            left.add_row("")
            left.add_row(f"[dim]Next Goal: {format_pillar_label(weakest_pillar)} ({weakest_level})[/dim]") # Keep a tiny nudge

            # Right Side: Context, Logs
            right = Table.grid(padding=0)
            
            # Active Context
            if active_kata_dir:
                status_color = "green" if in_kata_context else "dim"
                right.add_row(f"[bold]ACTIVE CONTEXT:[/bold] [{status_color}]{active_kata_dir.name}[/{status_color}]")
            else:
                right.add_row("[bold]ACTIVE CONTEXT:[/bold] [dim]Lobby[/dim]")
            
            right.add_row("")
            right.add_row("[bold]RECENT ACTIVITY:[/bold]")
            if recent_entries:
                tail = recent_entries[-3:]
                for proj, ts, note in tail:
                    right.add_row(f"[dim]• {proj} ({ts.split(' ')[0]}): {summarize_text(note, 30)}[/dim]")
            else:
                right.add_row("[dim]• No recent logs.[/dim]")

            top_grid.add_row(left, right)

            # Footer
            footer_text = f"\"karmanyeva adhikaras te ma phaleshu kadachana\""
            
            # Combine
            main_layout = Table.grid(expand=True)
            main_layout.add_row(top_grid)
            main_layout.add_row("") # Spacer
            main_layout.add_row(Align.center(f"[dim]{footer_text}[/dim]")) # Centered Quote


            resume_slug, resume_dir = resolve_last_kata(kata_root, notes_root)
            resume_label = "Resume Last Kata"
            if resume_slug:
                resume_label = f"Resume Last Kata ({resume_slug})"
            else:
                resume_label += " (none yet)"

            # --- Menu Options ---
            if in_kata_context:
                menu_options = [
                    ("Sensei Check (Run Tests)", "check"),
                    ("Sensei Watch Mode", "watch"),
                    ("Get Unstuck (Hint)", "hint"),
                    ("Peek This Kata (README/LOG)", "peek_current"),
                    ("Reset Kata", "reset_kata"),
                    ("Request Solution (Zero XP)", "solve_kata"),
                    ("Return to Lobby Menu", "return_lobby"),
                ]
            else:
                menu_options = [
                    ("Quick Train", "quick_train"),
                    ("Start New Session", "start_auto"),
                    (resume_label, "resume"),
                    ("Profile & History", "profile_history"),
                    ("Help & Workflow", "help"),
                    ("Exit", "exit"),
                ]
                if force_lobby_view and active_kata_dir:
                    menu_options.insert(-1, ("⬅️ Back to Kata Tools", "back_to_kata"))

            # Render Panel
            panel = Panel(
                main_layout,
                title="[bold white]NEXUS DOJO[/bold white]",
                subtitle=f"[italic grey62]Mastery through repetition[/italic grey62]",
                border_style="blue",
                box=box.ROUNDED,
                padding=(1, 2)
            )
            console.print(panel)
            console.print()

            for idx, (label, _) in enumerate(menu_options, start=1):
                console.print(f" [bold cyan]{idx}[/bold cyan] {label}")
            
            console.print()
            console.print(f"[italic grey50]Select an option [1-{len(menu_options)}]:[/italic grey50]", end=" ")
            
            choice = input().strip()
            
            # Map input to action
            try:
                idx = int(choice)
                if 1 <= idx <= len(menu_options):
                    action = menu_options[idx - 1][1]
                else:
                    console.print("[red]Invalid selection.[/red]")
                    time.sleep(1)
                    continue
            except ValueError:
                continue
        except Exception as e:
            console.print(f"[bold red]CRITICAL MENU ERROR: {e}[/bold red]")
            import traceback
            console.print(traceback.format_exc())
            # Add a pause so you can read the error before the loop clears the screen
            Prompt.ask("Press Enter to retry...")
            continue

        # --- Dispatcher ---
        if action == "exit":
            console.print(f"[blue]See you next time, {user_name}.[/blue]")
            return 0
            
        if action == "profile_history":
            handle_history(argparse.Namespace(root=str(kata_root), notes_root=str(notes_root)))
            Prompt.ask("\nPress Enter to return to menu")
            
        elif action == "help":
            handle_help(argparse.Namespace())

        elif action == "check":
            target_root = str(active_kata_dir.parent if active_kata_dir else kata_root)
            target_project = active_kata_dir.name if active_kata_dir else None
            handle_check(argparse.Namespace(
                project=target_project,
                root=target_root,
                notes_root=str(notes_root),
                truncate_output=True
            ))
            Prompt.ask("\nPress Enter to return to menu")
            
        elif action == "watch":
            target_root = str(active_kata_dir.parent if active_kata_dir else kata_root)
            target_project = active_kata_dir.name if active_kata_dir else None
            handle_watch(argparse.Namespace(
                project=target_project,
                root=target_root,
                notes_root=str(notes_root)
            ))
            
        elif action == "hint":
            if not active_kata_dir:
                console.print("[bold red]No active kata detected here.[/bold red]")
                time.sleep(1)
                continue
            question = Prompt.ask("Question focus (optional)", default="")
            handle_hint(
                argparse.Namespace(
                    project=active_kata_dir.name,
                    question=question,
                    provider=DEFAULT_IDEA_PROVIDER,
                    model=DEFAULT_IDEA_MODEL,
                    root=str(active_kata_dir.parent),
                    notes_root=str(notes_root),
                    dry_run=False,
                    offline=False,
                )
            )
            Prompt.ask("\nPress Enter to return to menu")

        elif action == "peek_current":
            if not active_kata_dir:
                console.print("[bold red]No active kata detected here.[/bold red]")
                time.sleep(1)
                continue
            peek_kata_summary(active_kata_dir, notes_root)
            Prompt.ask("\nPress Enter to return to menu")
            
        elif action == "reset_kata":
            if not active_kata_dir:
                console.print("[bold red]No active kata detected here.[/bold red]")
                time.sleep(1)
                continue
            handle_reset(argparse.Namespace(project=active_kata_dir.name, root=str(active_kata_dir.parent)))
            Prompt.ask("\nPress Enter to return to menu")

        elif action == "solve_kata":
            if not active_kata_dir:
                console.print("[bold red]No active kata detected here.[/bold red]")
                time.sleep(1)
                continue
            handle_solve(argparse.Namespace(project=active_kata_dir.name, root=str(active_kata_dir.parent)))
            Prompt.ask("\nPress Enter to return to menu")

        elif action == "return_lobby":
            force_lobby_view = True
            continue

        elif action == "back_to_kata":
            force_lobby_view = False
            continue

        elif action == "play":
            handle_play(argparse.Namespace())
            
        elif action == "solve":
            project = Prompt.ask("Kata slug")
            handle_solve(argparse.Namespace(project=project, root=str(kata_root)))
            Prompt.ask("\nPress Enter to return to menu")
            
        elif action == "reset":
            project = Prompt.ask("Kata slug")
            handle_reset(argparse.Namespace(project=project, root=str(kata_root)))
            Prompt.ask("\nPress Enter to return to menu")

        elif action == "dashboard":
            handle_dashboard(argparse.Namespace(root=str(kata_root), notes_root=str(notes_root)))
            Prompt.ask("\nPress Enter to return to menu")

        elif action == "continue":
            handle_continue(argparse.Namespace(root=str(kata_root), notes_root=str(notes_root)))
            Prompt.ask("\nPress Enter to return to menu")

        elif action == "resume":
            if not resume_slug:
                console.print("[yellow]No recent kata to resume yet. Start a new session first.[/yellow]")
                time.sleep(1.5)
                continue
            if not resume_dir or not resume_dir.exists():
                console.print(f"[red]Last kata '{resume_slug}' not found at {resume_dir}.[/red]")
                Prompt.ask("\nPress Enter to return to menu")
                continue
            # Concise summary panel
            mission = (resume_dir / "MISSION.md").read_text().splitlines() if (resume_dir / "MISSION.md").exists() else []
            readme = (resume_dir / "README.md").read_text().splitlines() if (resume_dir / "README.md").exists() else []
            mission_line = ""
            for line in mission:
                clean = re.sub(r"^#+\s*", "", line).strip()
                if clean:
                    mission_line = clean
                    break
            if mission_line:
                mission_line = re.sub(r"^Mission:\s*", "", mission_line, flags=re.IGNORECASE).strip()
            if not mission_line and readme:
                mission_line = readme[0].lstrip("# ").strip()
            last_log_raw = last_lines(resume_dir / "LOG.md", 1) if (resume_dir / "LOG.md").exists() else "No prior logs."
            last_log = summarize_text(last_log_raw.replace("\n", " "), 120)
            summary_body = (
                f"[bold]Kata:[/bold] {resume_dir.name}\n"
                f"[bold]Mission:[/bold] {mission_line or 'No mission summary.'}\n"
                f"[bold]Path:[/bold] {resume_dir.resolve()}\n"
                f"[bold]Last activity:[/bold] {last_log}"
            )
            console.print(Panel(summary_body, title="Resume Last Kata", border_style="cyan"))

            console.print("\n[bold]Choose an option:[/bold]")
            console.print(" [bold cyan]1[/bold cyan] Resume now")
            console.print(" [bold cyan]2[/bold cyan] Quick test preview, then resume")
            console.print(" [bold cyan]3[/bold cyan] Return to menu\n")
            choice = Prompt.ask(
                "[italic grey50]Select an option [1-3]:[/italic grey50]",
                choices=["1", "2", "3", ""],
                default="1",
                show_choices=False,
            ) or "1"
            if choice == "3":
                console.print("[dim]Returning to menu...[/dim]")
                time.sleep(0.8)
                continue
            if choice == "2":
                passed, summary = quick_check_preview(resume_dir, notes_root)
                style = "green" if passed else "red"
                console.print(Panel(summary, title="Test Preview", border_style=style))
                time.sleep(0.8)
            console.print("[dim]Launching...[/dim]")
            launch_session(resume_dir)
            continue

        elif action == "scaffold_refresh":
            project = Prompt.ask("Kata slug")
            if project:
                handle_scaffold_refresh(argparse.Namespace(project=project, root=str(kata_root)))
                Prompt.ask("\nPress Enter to return to menu")
            
        elif action == "start_auto":
            pillar = Prompt.ask("Focus pillar", choices=["python", "cli", "api", "testing", "mixed"], default="mixed")
            mode = Prompt.ask("Mode", choices=["script", "api"], default="script")
            template = "fastapi" if mode == "api" else "script"
            level = Prompt.ask("Difficulty", choices=["foundation", "proficient", "stretch"], default="foundation")

            with console.status("[bold green]Generating challenge idea...[/bold green]", spinner="dots"):
                idea, _ = pick_idea_with_hints(
                    provider=DEFAULT_IDEA_PROVIDER,
                    model=DEFAULT_IDEA_MODEL,
                    kata_root=kata_root,
                    notes_root=notes_root,
                    pillar_hint=pillar,
                    level_hint=level,
                    mode_hint=mode,
                    offline=False,
                )
                
            if not idea:
                console.print("[red]Could not generate an idea.[/red]")
                time.sleep(2)
                continue

            console.print(Panel(f"[bold]{idea}[/bold]", title="Proposed Kata", border_style="green"))
            
            if not Confirm.ask("Create this kata?", default=True):
                console.print("Cancelled.")
                continue

            with console.status("[bold green]Creating workspace...[/bold green]", spinner="dots"):
                handle_start(
                    argparse.Namespace(
                        idea=idea,
                        template=template,
                        root=str(kata_root),
                        notes_root=str(notes_root),
                        force=False,
                        pillar=pillar,
                        mode=mode,
                        level=level,
                        tests="edge",
                        guided=False,
                        reuse_settings=False,
                        yes=True,
                        scaffold="auto",
                        offline=False,
                    )
                )
            # handle_start prints next steps. We exit the menu so they can go code?
            # Or we loop back?
            # Typically user wants to exit menu to go to terminal.
            # But let's ask.
            if Confirm.ask("Exit menu to start coding?"):
                return 0

        elif action == "quick_train":
            # ... (Existing Quick Train Logic) ...
            # Reuse the vars we loaded at start of loop
            current_xp = skills.get(weakest_pillar, 0)
            level_title, _ = get_level_info(current_xp)
            # Map skill level to difficulty hint for idea picker
            difficulty = "foundation"
            if level_title == "Journeyman":
                difficulty = "proficient"
            elif level_title in {"Expert", "Master"}:
                difficulty = "stretch"
            
            target_mode = "fastapi" if weakest_pillar == "api" else "script"

            console.print("[dim]> Analyzing skill profile...[/dim]")
            rain_stop, rain_thread = start_matrix_rain(weakest_pillar, target_mode)
            try:
                idea, used_fallback = pick_idea_with_hints(
                    provider=DEFAULT_IDEA_PROVIDER,
                    model=DEFAULT_IDEA_MODEL,
                    kata_root=Path(DEFAULT_KATA_ROOT),
                    notes_root=Path(DEFAULT_NOTES_ROOT),
                    pillar_hint=weakest_pillar,
                    level_hint=difficulty,
                    mode_hint=target_mode,
                    offline=False,
                )
            finally:
                stop_matrix_rain(rain_stop, rain_thread)
            
            if not idea:
                console.print("[red]Could not generate an idea.[/red]")
                time.sleep(2)
                continue

            console.print(Panel(f"[bold]{idea}[/bold]", title=f"⚡ Quick Train: {weakest_pillar.title()} ({difficulty})", border_style="yellow"))
            
            console.print("[dim]Launching in 3 seconds... (Ctrl+C to cancel)[/dim]")
            try:
                time.sleep(3)
            except KeyboardInterrupt:
                continue

            handle_start(
                argparse.Namespace(
                    idea=idea,
                    template="fastapi" if target_mode == "fastapi" else "script",
                    root=str(DEFAULT_KATA_ROOT),
                    notes_root=str(DEFAULT_NOTES_ROOT),
                    force=False,
                    pillar=weakest_pillar,
                    mode=target_mode,
                    level=difficulty,
                    tests="edge",
                    guided=False,
                    reuse_settings=False,
                    yes=True, 
                    scaffold="auto",
                    offline=False,
                    launch=True, # Auto-launch
                )
            )
            # Auto-exit to let them code
            return 0


def handle_idea(args: argparse.Namespace) -> int:
    """
    Generate kata ideas from recent logs and calibrations.
    """
    kata_root = Path(args.root).expanduser()
    notes_root = Path(args.notes_root).expanduser()
    messages, weakest = build_idea_prompt(
        kata_root=kata_root,
        notes_root=notes_root,
        pillar_hint=getattr(args, "pillar", None),
        level_hint=getattr(args, "level", None),
        mode_hint=getattr(args, "mode", None),
    )

    if args.dry_run:
        print("System prompt:")
        print(messages[0]["content"])
        print("\nUser prompt:")
        print(messages[1]["content"])
        return 0

    idea_content = call_idea_api(
        provider=args.provider,
        model=args.model,
        messages=messages,
    )
    idea = parse_idea_content(idea_content) if idea_content else None
    used_fallback = False
    if not idea:
        idea = fallback_idea(
            pillar_hint=getattr(args, "pillar", None),
            level_hint=getattr(args, "level", None),
            mode_hint=getattr(args, "mode", None),
        )
        used_fallback = bool(idea)
    if not idea:
        print("Idea generation failed. Check your API key and network.", file=sys.stderr)
        return 1
    idea = normalize_idea_line(idea)

    print(f"Weakest pillar (from calibrations): {weakest or 'unknown'}")
    if used_fallback:
        print("Model unavailable; showing curated fallback.")
    print("Suggested ideas:")
    print(idea)
    return 0


def append_line(path: Path, line: str) -> None:
    """
    Append a line to a file, creating the file if needed.
    """
    with path.open("a", encoding="utf-8") as handle:
        handle.write(line)


def get_profiles_dir(notes_root: Path) -> Path:
    path = notes_root / "profiles"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_current_profile_name(notes_root: Path) -> Optional[str]:
    pointer = notes_root / ".current_profile"
    if pointer.exists():
        name = pointer.read_text().strip()
        return name or None
    return None


def set_current_profile_name(notes_root: Path, name: str) -> None:
    notes_root.mkdir(parents=True, exist_ok=True)
    (notes_root / ".current_profile").write_text(name.strip())


def clear_current_profile(notes_root: Path) -> None:
    pointer = notes_root / ".current_profile"
    if pointer.exists():
        pointer.unlink()


def list_profiles(notes_root: Path) -> list[str]:
    profiles_dir = get_profiles_dir(notes_root)
    return sorted(p.stem for p in profiles_dir.glob("*.json") if p.is_file())


def load_settings(notes_root: Path) -> dict[str, str]:
    """
    Load persisted guided start settings for the active profile (falls back to legacy file).
    """
    profiles_dir = get_profiles_dir(notes_root)
    current = get_current_profile_name(notes_root)
    if current:
        profile_path = profiles_dir / f"{current}.json"
        if profile_path.exists():
            try:
                return json.loads(profile_path.read_text())
            except json.JSONDecodeError:
                return {}
    # Legacy fallback
    settings_path = notes_root / "dojo_settings.json"
    if settings_path.exists():
        try:
            data = json.loads(settings_path.read_text())
        except json.JSONDecodeError:
            return {}
        # Promote legacy settings into a default profile
        current = current or "default"
        set_current_profile_name(notes_root, current)
        save_settings(notes_root, data)
        return data
    return {}


def save_settings(notes_root: Path, settings: dict[str, str]) -> None:
    """
    Persist guided start settings for the active profile (and mirror to legacy file).
    """
    profiles_dir = get_profiles_dir(notes_root)
    current = get_current_profile_name(notes_root)
    if not current:
        current = "default"
        set_current_profile_name(notes_root, current)
    profile_path = profiles_dir / f"{current}.json"
    profile_path.write_text(json.dumps(settings, indent=2))
    # Legacy mirror for compatibility
    legacy_path = notes_root / "dojo_settings.json"
    legacy_path.write_text(json.dumps(settings, indent=2))


def prompt_choice(prompt: str, default: str, allowed: set[str]) -> str:
    """
    Prompt the user for a choice with validation and an explicit default.
    """
    allowed_lower = {item.lower() for item in allowed}
    while True:
        choice = input(prompt).strip().lower()
        if not choice:
            return default.lower()
        if choice in allowed_lower:
            return choice
        print(
            f"Invalid choice. Pick one of: {', '.join(sorted(allowed_lower))}. "
            f"Default is {default}; press Enter to accept it."
        )


def sanitize_profile_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "", name).strip()


def ensure_profile_selected(notes_root: Path) -> str:
    """
    Ensure there is an active profile; prompt to create or switch if none.
    """
    notes_root.mkdir(parents=True, exist_ok=True)
    profiles_dir = get_profiles_dir(notes_root)
    current = get_current_profile_name(notes_root)
    if current and (profiles_dir / f"{current}.json").exists():
        return current

    existing = list_profiles(notes_root)
    console.print(Panel("No active profile found. Create or select a profile to continue.", border_style="cyan"))

    if not existing:
        name = sanitize_profile_name(Prompt.ask("Enter a profile name", default="engineer"))
        if not name:
            name = "engineer"
        set_current_profile_name(notes_root, name)
        save_settings(notes_root, {"user_name": name})
        console.print(f"[green]Profile '{name}' created and set active.[/green]")
        return name

    console.print("Existing profiles:")
    for prof in existing:
        console.print(f" - {prof}")
    choice = Prompt.ask(
        "Choose: 1) Create new  2) Use existing",
        choices=["1", "2"],
        default="2",
        show_choices=False,
    )
    if choice == "1":
        name = sanitize_profile_name(Prompt.ask("Enter a profile name", default="engineer"))
        if not name:
            name = "engineer"
        set_current_profile_name(notes_root, name)
        save_settings(notes_root, {"user_name": name})
        console.print(f"[green]Profile '{name}' created and set active.[/green]")
        return name
    else:
        target = Prompt.ask("Enter profile name to use", choices=existing, default=existing[0])
        set_current_profile_name(notes_root, target)
        console.print(f"[green]Switched to profile '{target}'.[/green]")
        return target


def collect_entries(kata_root: Path, notes_root: Path, since: datetime) -> list[tuple[str, str, str]]:
    """
    Collect log entries from kata logs and central log since a cutoff.
    """
    entries: list[tuple[str, str, str]] = []

    central_log = notes_root / "log.md"
    if central_log.exists():
        entries.extend(parse_log_file(central_log, default_project="central", since=since))

    if kata_root.exists():
        for project_dir in kata_root.iterdir():
            if project_dir.is_dir():
                project_log = project_dir / "LOG.md"
                if project_log.exists():
                    entries.extend(parse_log_file(project_log, default_project=project_dir.name, since=since))

    # Sort chronologically
    entries.sort(key=lambda item: item[1])
    deduped: list[tuple[str, str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for entry in entries:
        if entry not in seen:
            deduped.append(entry)
            seen.add(entry)
    return deduped


def count_completed_drills(kata_root: Path, notes_root: Path) -> int:
    """
    Count distinct kata projects that have history entries (excludes central log only entries).
    """
    entries = collect_entries(kata_root, notes_root, datetime.min)
    projects = {project for project, _, _ in entries if project and project != "central"}
    return len(projects)


def quick_check_preview(project_dir: Path, notes_root: Path) -> tuple[bool, str]:
    """
    Run a lightweight unittest check and return (passed, summary).
    """
    if not (project_dir / "tests").exists():
        return False, "No tests folder found."
    install_dependencies(project_dir)
    result = subprocess.run(
        [sys.executable, "-m", "unittest"],
        cwd=project_dir,
        capture_output=True,
        text=True
    )
    output = result.stderr or result.stdout
    summary = summarize_failure_output(output)
    if result.returncode == 0:
        return True, "Tests passed in preview."
    return False, summary or "Tests failed (no output captured)."


def peek_kata_summary(project_dir: Path, notes_root: Path) -> None:
    """
    Display a compact summary of a kata without launching the session.
    """
    readme = (project_dir / "README.md").read_text().splitlines() if (project_dir / "README.md").exists() else []
    mission = (project_dir / "MISSION.md").read_text().splitlines() if (project_dir / "MISSION.md").exists() else []
    log_hint = last_lines(project_dir / "LOG.md", 3) if (project_dir / "LOG.md").exists() else "No project log yet."
    def strip_heading(line: str) -> str:
        return re.sub(r"^#+\s*", "", line).strip()
    mission_excerpt = "\n".join(strip_heading(line) for line in mission[:8]) if mission else "MISSION.md missing."
    readme_title = readme[0].lstrip("# ").strip() if readme else "README missing."

    body = (
        f"[bold]Path:[/bold] {project_dir.resolve()}\n"
        f"[bold]README:[/bold] {readme_title}\n\n"
        f"[bold]Recent log:[/bold]\n{log_hint}"
    )
    console.print(Panel(body, title=f"📄 {project_dir.name}", border_style="cyan"))
    console.print("[bold]MISSION excerpt:[/bold]")
    type_out_text(mission_excerpt)


def build_idea_prompt(
    kata_root: Path,
    notes_root: Path,
    pillar_hint: Optional[str] = None,
    level_hint: Optional[str] = None,
    mode_hint: Optional[str] = None,
) -> tuple[list[dict[str, str]], Optional[str]]:
    """
    Build messages for the idea picker and determine weakest pillar.
    """
    rubric_path = notes_root / "rubric.md"
    rubric_text = rubric_path.read_text() if rubric_path.exists() else ""

    logs_path = notes_root / "log.md"
    logs_snippet = last_lines(logs_path, 10) if logs_path.exists() else "No logs yet."

    cal_path = notes_root / "calibrations.md"
    calib_scores = parse_calibrations(cal_path) if cal_path.exists() else {}
    weakest = weakest_pillar(calib_scores)
    calib_text = ", ".join(f"{pillar}:{score}" for pillar, score in calib_scores.items()) or "none"

    katas = list_katas(kata_root)
    katas_text = ", ".join(katas) if katas else "none"

    fallback_line = fallback_idea(
        pillar_hint=pillar_hint,
        level_hint=level_hint,
        mode_hint=mode_hint,
    ) or "IDEA: Unit converter -- CLI to convert units with input validation."

    system = (
        "You are the NexusDojo idea picker. Return ONE idea only in this exact format:\n"
        "IDEA: <short title> -- <1 sentence spec>\n"
        "Keep it runnable in under a few hours. No prefacing text. No extra bullets.\n"
        f"If you cannot generate from context, emit this fallback verbatim: {strip_idea_prefix(fallback_line)}"
    )
    user = (
        f"Weakest pillar: {weakest or 'unknown'}\n"
        f"Pillar hint: {pillar_hint or 'unspecified'}\n"
        f"Level hint: {level_hint or 'unspecified'}\n"
        f"Mode hint: {mode_hint or 'unspecified'}\n"
        f"Calibration scores: {calib_text}\n"
        f"Existing katas: {katas_text}\n"
        f"Recent logs (latest 10 lines):\n{logs_snippet}\n"
        f"Rubric:\n{rubric_text}\n"
        "Return exactly one line starting with 'IDEA:' and nothing else."
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}], weakest


def build_idea_prompt_multi(
    kata_root: Path,
    notes_root: Path,
    pillar_hint: Optional[str],
    level_hint: Optional[str],
    mode_hint: Optional[str],
    max_options: int,
) -> tuple[list[dict[str, str]], Optional[str]]:
    """
    Build messages that request a short list of kata ideas.
    """
    messages, weakest = build_idea_prompt(
        kata_root=kata_root,
        notes_root=notes_root,
        pillar_hint=pillar_hint,
        level_hint=level_hint,
        mode_hint=mode_hint,
    )
    system = (
        "You are the NexusDojo idea picker. Return up to "
        f"{max_options} ideas as bullet lines. Each line MUST start with "
        "'IDEA:' then a short title, then '--' then a one-sentence spec. "
        "No intro or outro text."
    )
    user_lines = [line for line in messages[1]["content"].splitlines() if not line.startswith("Return")]
    user_lines.append(
        f"Return up to {max_options} lines, each starting with 'IDEA:' and containing a one-sentence spec."
    )
    messages[0]["content"] = system
    messages[1]["content"] = "\n".join(user_lines)
    return messages, weakest


def build_hint_prompt(project_dir: Path, notes_root: Path, question: str) -> list[dict[str, str]]:
    """
    Build messages for the hint generator with local context.
    """
    readme = (project_dir / "README.md").read_text() if (project_dir / "README.md").exists() else ""
    recent_log = last_lines(project_dir / "LOG.md", 5) if (project_dir / "LOG.md").exists() else "No project log yet."
    central_log = last_lines(notes_root / "log.md", 5) if (notes_root / "log.md").exists() else ""
    calib = parse_calibrations(notes_root / "calibrations.md") if (notes_root / "calibrations.md").exists() else {}
    weakest = weakest_pillar(calib)

    system = (
        "You are the NexusDojo mentor. Return a concise hint only. Keep it high-signal, no fluff.\n"
        "- Format: up to 3 bullets, max 80 chars each.\n"
        "- Prefer: next action, quick check, and 1 edge-case to test.\n"
        "- Avoid: full solutions; be specific and terse."
    )
    user = (
        f"Project: {project_dir.name}\n"
        f"Weakest pillar: {weakest or 'unknown'}\n"
        f"Question: {question or 'What should I do next?'}\n"
        f"README snippet:\n{readme[:800]}\n"
        f"Recent project log:\n{recent_log}\n"
        f"Recent central log:\n{central_log}\n"
        "Respond with bullets only."
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def build_test_hint_prompt(project_dir: Path, notes_root: Path, max_hints: int) -> list[dict[str, str]]:
    """
    Build messages for generating edge-case test hints.
    """
    readme = (project_dir / "README.md").read_text() if (project_dir / "README.md").exists() else ""
    recent_log = last_lines(project_dir / "LOG.md", 5) if (project_dir / "LOG.md").exists() else "No project log yet."
    system = (
        "You are the NexusDojo test coach. Propose edge cases to test.\n"
        f"- Return a bullet list (one line each), max {max_hints} items.\n"
        "- Focus on failure modes, boundary values, and validation paths.\n"
        "- No implementation, only descriptions."
    )
    user = (
        f"Project: {project_dir.name}\n"
        f"README snippet:\n{readme[:800]}\n"
        f"Recent project log:\n{recent_log}\n"
        "List only edge cases to test."
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def generate_with_progress(
    task_name: str,
    provider: str,
    model: str,
    messages: list[dict[str, str]]
) -> Optional[str]:
    """
    Wraps call_idea_api with a nice multi-step progress spinner.
    """
    steps = [
        "Analyzing request...",
        "Consulting the archives...",
        "Drafting response...",
        "Refining logic...",
        "Finalizing output..."
    ]
    
    # Since we can't update text during the blocking call easily without threads,
    # we'll just show a nice indeterminate spinner with a fixed title, 
    # but initially cycle a few messages to show "life".
    # Actually, let's just use a nice bold spinner.
    
    with console.status(f"[bold green]{task_name}...[/bold green]", spinner="dots") as status:
        # We can't cycle messages during urlopen block.
        # But we can simulate "Thinking" start.
        time.sleep(0.5)
        status.update(f"[bold green]{task_name}: Connecting to {provider}...[/bold green]")
        return call_idea_api(provider, model, messages)


def call_idea_api(provider: str, model: str, messages: list[dict[str, str]]) -> Optional[str]:
    """
    Call the selected provider to get idea suggestions.
    """
    if provider == "ollama":
        payload = json.dumps(
            {"model": model, "messages": messages, "stream": False}
        ).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        request = urllib.request.Request(
            OLLAMA_URL,
            data=payload,
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as resp:
                raw = resp.read()
                data = json.loads(raw.decode("utf-8"))
                content = ""
                if isinstance(data, dict):
                    content = data.get("message", {}).get("content", "") or data.get("response", "")
        except (urllib.error.URLError, urllib.error.HTTPError) as exc:
            print(f"API call failed: {exc}", file=sys.stderr)
            return None
        except (json.JSONDecodeError, IndexError, AttributeError):
            print("Unexpected API response shape.", file=sys.stderr)
            return None
    elif provider == "openrouter":
        api_key = os.environ.get("NEXUSDOJO_API_KEY")
        if not api_key:
            print("Missing NEXUSDOJO_API_KEY env var.", file=sys.stderr)
            return None

        payload = json.dumps({"model": model, "messages": messages}).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        request = urllib.request.Request(
            OPENROUTER_URL,
            data=payload,
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=120) as resp:
                raw = resp.read()
                data = json.loads(raw.decode("utf-8"))
                content = (
                    data.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                )
        except (urllib.error.URLError, urllib.error.HTTPError) as exc:
            print(f"API call failed: {exc}", file=sys.stderr)
            return None
        except (json.JSONDecodeError, IndexError, AttributeError):
            print("Unexpected API response shape.", file=sys.stderr)
            return None
    else:
        print(f"Unsupported provider: {provider}", file=sys.stderr)
        return None

    if not content:
        print("Empty idea content returned.", file=sys.stderr)
        return None
    return content.strip()


def parse_calibrations(path: Path) -> dict[str, int]:
    """
    Parse calibration scores per pillar; returns latest score per pillar.
    """
    scores: dict[str, int] = {}
    for line in path.read_text().splitlines():
        if "pillar=" not in line or "score=" not in line:
            continue
        try:
            parts = line.split()
            pillar_part = next(p for p in parts if p.startswith("pillar="))
            score_part = next(p for p in parts if p.startswith("score="))
            pillar = pillar_part.split("=", 1)[1]
            score = int(score_part.split("=", 1)[1])
            scores[pillar] = score
        except (StopIteration, ValueError):
            continue
    return scores


def weakest_pillar(scores: dict[str, int]) -> Optional[str]:
    """
    Pick the pillar with the lowest score; ties resolved arbitrarily.
    """
    if not scores:
        return None
    return min(scores.items(), key=lambda item: item[1])[0]


def list_katas(kata_root: Path) -> list[str]:
    """
    List existing kata slugs.
    """
    if not kata_root.exists():
        return []
    return sorted([p.name for p in kata_root.iterdir() if p.is_dir()])


def last_lines(path: Path, n: int) -> str:
    """
    Return the last n lines from a file as a single string.
    """
    lines = path.read_text().splitlines()
    return "\n".join(lines[-n:])


def pick_idea(provider: str, model: str, kata_root: Path, notes_root: Path) -> Optional[str]:
    """
    Generate ideas and pick the first bullet as the selected idea.
    """
    messages, _ = build_idea_prompt(kata_root=kata_root, notes_root=notes_root)
    content = call_idea_api(provider=provider, model=model, messages=messages)
    idea = parse_idea_content(content) if content else None
    if idea:
        return idea
    return None


def pick_idea_with_hints(
    provider: str,
    model: str,
    kata_root: Path,
    notes_root: Path,
    pillar_hint: Optional[str],
    level_hint: Optional[str],
    mode_hint: Optional[str],
    offline: bool = False,
) -> tuple[Optional[str], bool]:
    """
    Generate an idea using hints; fall back to canned ideas if needed.
    """
    if offline:
        return fallback_idea(pillar_hint=pillar_hint, level_hint=level_hint, mode_hint=mode_hint), True
    messages, _ = build_idea_prompt(
        kata_root=kata_root,
        notes_root=notes_root,
        pillar_hint=pillar_hint,
        level_hint=level_hint,
        mode_hint=mode_hint,
    )
    content = generate_with_progress("Generating Idea", provider, model, messages)
    idea = parse_idea_content(content) if content else None
    if idea:
        return idea, False
    return fallback_idea(pillar_hint=pillar_hint, level_hint=level_hint, mode_hint=mode_hint), True


def pick_idea_options(
    provider: str,
    model: str,
    kata_root: Path,
    notes_root: Path,
    pillar_hint: Optional[str],
    level_hint: Optional[str],
    mode_hint: Optional[str],
    max_options: int = 3,
    offline: bool = False,
) -> tuple[list[str], bool]:
    """
    Generate a short list of ideas; fall back to curated options.
    """
    if offline:
        return fallback_idea_options(
            pillar_hint=pillar_hint,
            level_hint=level_hint,
            mode_hint=mode_hint,
            max_options=max_options,
        ), True
    messages, _ = build_idea_prompt_multi(
        kata_root=kata_root,
        notes_root=notes_root,
        pillar_hint=pillar_hint,
        level_hint=level_hint,
        mode_hint=mode_hint,
        max_options=max_options,
    )
    content = call_idea_api(provider=provider, model=model, messages=messages)
    options = parse_idea_options(content, max_options) if content else []
    if options:
        return options[:max_options], False
    return fallback_idea_options(
        pillar_hint=pillar_hint,
        level_hint=level_hint,
        mode_hint=mode_hint,
        max_options=max_options,
    ), True


def parse_idea_content(content: Optional[str]) -> Optional[str]:
    """
    Extract a single idea line from model output.
    """
    if not content:
        return None
    for line in content.splitlines():
        cleaned = line.strip()
        if not cleaned:
            continue
        if cleaned.lower().startswith("idea:"):
            return normalize_idea_line(cleaned)
        if cleaned.startswith(("-", "*", "•")):
            cleaned = cleaned.lstrip("-*• ").strip()
        if cleaned:
            return normalize_idea_line(cleaned)
    return None


def parse_idea_options(content: Optional[str], max_options: int) -> list[str]:
    """
    Extract multiple idea lines from model output.
    """
    if not content:
        return []
    options: list[str] = []
    for line in parse_bullet_list(content):
        cleaned = line.strip()
        if not cleaned:
            continue
        options.append(normalize_idea_line(cleaned))
        if len(options) >= max_options:
            break
    if not options:
        solo = parse_idea_content(content)
        if solo:
            options.append(normalize_idea_line(solo))
    return options


def fallback_idea(
    pillar_hint: Optional[str],
    level_hint: Optional[str],
    mode_hint: Optional[str],
) -> Optional[str]:
    """
    Provide a deterministic idea if the model call fails.
    """
    pillar = pillar_hint or "mixed"
    level = level_hint or "foundation"
    mode = mode_hint or "script"

    ideas = {
        ("python", "foundation"): "IDEA: Basic calculator -- Build add/subtract/multiply/divide CLI with input validation.",
        ("python", "proficient"): "IDEA: CSV summarizer -- Load a CSV and print min/max/avg for numeric columns.",
        ("python", "stretch"): "IDEA: Config loader -- Parse a YAML/JSON config and validate required fields.",
        ("cli", "foundation"): "IDEA: TODO CLI -- Add/list/complete tasks stored in a local JSON file.",
        ("cli", "proficient"): "IDEA: Log filter CLI -- Filter a log file by level/date and print matches.",
        ("cli", "stretch"): "IDEA: Bulk rename CLI -- Rename files by pattern with dry-run support.",
        ("api", "foundation"): "IDEA: Health + echo API -- Two endpoints: /health and /echo?msg=...",
        ("api", "proficient"): "IDEA: Notes API -- CRUD notes in memory with basic validation.",
        ("api", "stretch"): "IDEA: Shortlink API -- Create/read/delete shortlinks in memory with collision checks.",
        ("testing", "foundation"): "IDEA: String utils tests -- Write and test a couple of string helper functions.",
        ("testing", "proficient"): "IDEA: Input validator tests -- Implement and test input validation functions.",
        ("testing", "stretch"): "IDEA: File ops tests -- Implement file read/write helpers with edge-case tests.",
        ("mixed", "foundation"): "IDEA: Unit converter -- CLI to convert units (km/mi, kg/lb) with simple tests.",
        ("mixed", "proficient"): "IDEA: Markdown heading extractor -- CLI to list headings from a .md file.",
        ("mixed", "stretch"): "IDEA: Simple RPN calculator -- CLI with stack ops and tests.",
    }
    key = (pillar, level)
    idea = ideas.get(key) or ideas.get(("mixed", level)) or ideas.get(("mixed", "foundation"))
    if mode == "api" and "API" not in idea:
        idea = ideas.get(("api", level)) or idea
    return idea


def fallback_idea_options(
    pillar_hint: Optional[str],
    level_hint: Optional[str],
    mode_hint: Optional[str],
    max_options: int,
) -> list[str]:
    """
    Provide a small set of deterministic idea options.
    """
    choices: list[str] = []
    attempts = [
        (pillar_hint, level_hint, mode_hint),
        (pillar_hint, "foundation", mode_hint),
        ("mixed", level_hint, mode_hint),
        ("mixed", "foundation", mode_hint),
        ("python", "foundation", "script"),
    ]
    for pillar, level, mode in attempts:
        idea = fallback_idea(pillar_hint=pillar, level_hint=level, mode_hint=mode)
        if idea and idea not in choices:
            choices.append(idea)
        if len(choices) >= max_options:
            break
    if not choices:
        choices.append("IDEA: Unit converter -- CLI to convert units with validation.")
    return choices[:max_options]


def latest_activity(kata_root: Path, notes_root: Path) -> Optional[tuple[str, str, str]]:
    """
    Return the most recent activity entry across central and kata logs.
    """
    entries = collect_entries(kata_root, notes_root, datetime.min)
    return entries[-1] if entries else None


def calibration_trend(path: Path) -> dict[str, int]:
    """
    Compute score deltas per pillar from calibration history.
    """
    deltas: dict[str, list[int]] = {}
    for line in path.read_text().splitlines():
        if "pillar=" not in line or "score=" not in line:
            continue
        try:
            parts = line.split()
            pillar = next(p for p in parts if p.startswith("pillar=")).split("=", 1)[1]
            score = int(next(p for p in parts if p.startswith("score=")).split("=", 1)[1])
        except (StopIteration, ValueError):
            continue
        deltas.setdefault(pillar, []).append(score)
    return {pillar: scores[-1] - scores[0] for pillar, scores in deltas.items() if len(scores) >= 2}


def practice_balance(scores: dict[str, int]) -> str:
    """
    Render a compact balance string from calibration scores.
    """
    if not scores:
        return ""
    ordered = ["python", "cli", "api", "testing"]
    parts = [f"{pillar}:{scores[pillar]}" for pillar in ordered if pillar in scores]
    missing = [p for p in ordered if p not in scores]
    if missing:
        parts.append(f"missing:{','.join(missing)}")
    return " | ".join(parts)


def parse_log_file(path: Path, default_project: str, since: datetime) -> list[tuple[str, str, str]]:
    """
    Parse log entries of the form "- [YYYY-MM-DD HH:MM] note".
    """
    parsed: list[tuple[str, str, str]] = []
    for line in path.read_text().splitlines():
        if not line.startswith("- ["):
            continue
        try:
            ts_part, note_part = line[3:].split("]", 1)
            ts = datetime.strptime(ts_part.strip(), "%Y-%m-%d %H:%M")
        except ValueError:
            continue
        if ts < since:
            continue
        note = note_part.strip()
        # Remove leading colon if present from central log formatting.
        if note.startswith(":"):
            note = note[1:].strip()
        project = default_project
        if ":" in note:
            possible_project, maybe_note = note.split(":", 1)
            if possible_project and " " not in possible_project:
                project = possible_project
                note = maybe_note.strip()
        parsed.append((project, ts.strftime("%Y-%m-%d %H:%M"), note))
    return parsed


def summarize_text(text: str, limit: int = 160) -> str:
    """
    Lightweight summarization by truncating and condensing whitespace.
    """
    cleaned = " ".join(text.split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 3].rstrip() + "..."


def fallback_hint(question: str) -> str:
    """
    Provide a deterministic hint when models are unavailable.
    """
    base = [
        "- Run the existing tests to see failures before coding.",
        "- Check inputs: empty, None, wrong types, and out-of-range values.",
        "- Log one insight to LOG.md after each change to keep momentum.",
    ]
    if question:
        base.insert(0, f"- Re-read your question: {summarize_text(question, 60)}")
    return "\n".join(base[:3])


def parse_bullet_list(content: Optional[str]) -> list[str]:
    """
    Parse a simple bullet list from model output.
    """
    if not content:
        return []
    hints: list[str] = []
    for line in content.splitlines():
        cleaned = line.strip()
        if not cleaned:
            continue
        if cleaned.startswith(("-", "*", "•")):
            cleaned = cleaned.lstrip("-*• ").strip()
        hints.append(cleaned)
    return hints


def load_hint_history(notes_root: Path) -> dict[str, list[str]]:
    """
    Load hint usage history.
    """
    log_path = notes_root / "hints_log.json"
    if not log_path.exists():
        return {}
    try:
        data = json.loads(log_path.read_text())
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def prune_hint_history(history: dict[str, list[str]], now: datetime) -> dict[str, list[str]]:
    """
    Remove entries older than 24h.
    """
    pruned: dict[str, list[str]] = {}
    for project, timestamps in history.items():
        filtered: list[str] = []
        for ts in timestamps:
            try:
                dt = datetime.fromisoformat(ts)
            except ValueError:
                continue
            if now - dt <= timedelta(days=1):
                filtered.append(ts)
        if filtered:
            pruned[project] = filtered
    return pruned


def hint_quota_remaining(notes_root: Path, project: Optional[str]) -> int:
    """
    Compute remaining hints for a project in the last 24h.
    """
    now = datetime.now()
    history = prune_hint_history(load_hint_history(notes_root), now)
    count = len(history.get(project or "", []))
    return max(0, HINT_MAX_PER_DAY - count)


def count_hints_today(notes_root: Path) -> int:
    """
    Count total hints used today across all projects.
    """
    now = datetime.now()
    history = prune_hint_history(load_hint_history(notes_root), now)
    total = 0
    for timestamps in history.values():
        total += len(timestamps)
    return total


def check_hint_rate_limit(project: str, notes_root: Path) -> tuple[bool, str, int]:
    """
    Enforce a short debounce for hint pulls. Daily limit is effectively unlimited.
    """
    log_path = notes_root / "hints_log.json"
    notes_root.mkdir(parents=True, exist_ok=True)
    now = datetime.now()
    history = prune_hint_history(load_hint_history(notes_root), now)
    log_path.write_text(json.dumps(history, indent=2))
    
    project_entries = []
    for ts in history.get(project, []):
        try:
            project_entries.append(datetime.fromisoformat(ts))
        except ValueError:
            continue
            
    if project_entries:
        last_ts = max(project_entries)
        elapsed = (now - last_ts).total_seconds()
        if elapsed < HINT_COOLDOWN_SECONDS:
            wait_for = int(HINT_COOLDOWN_SECONDS - elapsed)
            return False, f"Debouncing... wait {wait_for}s.", 999
            
    return True, "Ready", 999


def record_hint_use(project: str, notes_root: Path) -> None:
    """
    Record a hint usage timestamp for rate limiting.
    """
    notes_root.mkdir(parents=True, exist_ok=True)
    log_path = notes_root / "hints_log.json"
    now_dt = datetime.now()
    history = prune_hint_history(load_hint_history(notes_root), now_dt)
    now = datetime.now().isoformat(timespec="seconds")
    history.setdefault(project, []).append(now)
    log_path.write_text(json.dumps(history, indent=2))


def fallback_edge_hints(project_dir: Path) -> list[str]:
    """
    Provide deterministic edge-case hints based on template.
    """
    readme_text = (project_dir / "README.md").read_text() if (project_dir / "README.md").exists() else ""
    template = "fastapi" if "Template: fastapi" in readme_text else "script"
    if template == "fastapi":
        return [
            "Missing/empty query params for echo endpoint",
            "Non-JSON request body and error handling",
            "Invalid UTF-8 input and response encoding",
            "Large payload handling or timeouts",
        ]
    return [
        "Empty or whitespace-only input",
        "Non-numeric or malformed arguments",
        "File-not-found paths and permission errors",
        "Upper/lower bounds and overflow/underflow",
    ]


def write_edge_hint_tests(project_dir: Path, hints: list[str]) -> None:
    """
    Materialize edge-case hints as skipped tests for fast activation.
    """
    tests_dir = project_dir / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)
    (tests_dir / "__init__.py").write_text("", encoding="utf-8")
    target = tests_dir / "test_edge_hints.py"
    lines = [
        '"""Auto-generated edge-case TODOs. Safe to edit."""',
        "import unittest",
        "",
        "class EdgeHintTests(unittest.TestCase):",
    ]
    for idx, hint in enumerate(hints, start=1):
        safe_hint = summarize_text(hint, 80).replace("'", "\"")
        lines.extend(
            [
                f"    @unittest.skip('Edge hint: {safe_hint}')",
                f"    def test_hint_{idx}(self) -> None:",
                "        self.fail('Implement this edge case')",
                "",
            ]
        )
    target.write_text("\n".join(lines), encoding="utf-8")


def apply_placeholders(path: Path, replacements: dict[str, str]) -> None:
    """
    Replace {{KEY}} placeholders in a text file with provided values.
    """
    text = path.read_text()
    for key, value in replacements.items():
        text = text.replace(f"{{{{{key}}}}}", value)
    path.write_text(text)


def slugify(text: str) -> str:
    """
    Convert free text to a filesystem-safe slug.
    """
    if "--" in text:
        text = text.split("--", 1)[0]
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug


def next_available_slug(base_slug: str, kata_root: Path) -> str:
    """
    Find the next available slug by appending an incrementing suffix.
    """
    candidate = base_slug
    suffix = 2
    while (kata_root / candidate).exists():
        candidate = f"{base_slug}-{suffix}"
        suffix += 1
    return candidate


def apply_placeholders_tree(root: Path, replacements: dict[str, str]) -> None:
    """
    Apply placeholder replacements to all text files under a root directory.
    """
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.name.startswith(".") or path.suffix in {".pyc"}:
            continue
        try:
            content = path.read_text()
        except (OSError, UnicodeDecodeError):
            continue
        updated = content
        for key, value in replacements.items():
            updated = updated.replace(f"{{{{{key}}}}}", value)
        if updated != content:
            path.write_text(updated)


def resolve_template(template: str, mode_hint: Optional[str]) -> str:
    """
    Normalize the template choice from CLI and mode hints.
    """
    if mode_hint == "api":
        return "fastapi"
    return template


def normalize_idea_line(content: str) -> str:
    """
    Normalize an idea to a single 'IDEA: title -- spec' line.
    """
    cleaned = (content or "").strip()
    if not cleaned:
        cleaned = "Untitled kata"
    if cleaned.lower().startswith("idea:"):
        cleaned = cleaned.split(":", 1)[1].strip()
    if "--" not in cleaned:
        cleaned = cleaned.replace("  ", " ")
        cleaned = f"{cleaned} -- crisp spec"
    normalized = cleaned if cleaned.lower().startswith("idea:") else f"IDEA: {cleaned}"
    return normalized.strip()


def strip_idea_prefix(content: str) -> str:
    """
    Remove the leading IDEA: label if present.
    """
    cleaned = (content or "").strip()
    if cleaned.lower().startswith("idea:"):
        return cleaned.split(":", 1)[1].strip()
    return cleaned


def generate_scaffold_spec(
    idea_line: str,
    pillar_hint: Optional[str],
    level_hint: Optional[str],
    template: str,
    offline: bool = False,
) -> tuple[dict[str, Any], bool]:
    """
    Generate a scaffold spec using the default idea provider with safe fallback.
    """
    if offline:
        return fallback_scaffold_spec(idea_line, template=template), True
    messages = build_scaffold_prompt(
        idea_line=idea_line,
        pillar_hint=pillar_hint,
        level_hint=level_hint,
        template=template,
    )
    content = call_idea_api(
        provider=DEFAULT_IDEA_PROVIDER,
        model=DEFAULT_IDEA_MODEL,
        messages=messages,
    )
    spec = parse_scaffold_spec(content) if content else None
    fallback_used = False
    if not spec:
        spec = fallback_scaffold_spec(idea_line, template=template)
        fallback_used = True
    return spec, fallback_used


def build_scaffold_prompt(
    idea_line: str,
    pillar_hint: Optional[str],
    level_hint: Optional[str],
    template: str,
) -> list[dict[str, str]]:
    """
    Ask the model for a structured kata scaffold (JSON only).
    """
    idea_title = strip_idea_prefix(idea_line)
    system = (
        "You are the NexusDojo scaffold builder. Return ONLY a JSON object with keys:\n"
        "- title (string), summary (string), idea (string)\n"
        "- functions: list of objects {name, signature, description, example, edge_cases}\n"
        "- example: {args: list, kwargs: object, output: JSON-serializable}\n"
        "Keep examples small and deterministic. No code fences, no prose, JSON only."
    )
    user = (
        f"Idea: {idea_title}\n"
        f"Pillar hint: {pillar_hint or 'mixed'}\n"
        f"Level hint: {level_hint or 'foundation'}\n"
        f"Template: {template}\n"
        "Return JSON only."
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def parse_scaffold_spec(content: Optional[str]) -> Optional[dict[str, Any]]:
    """
    Parse scaffold JSON from model output.
    """
    if not content:
        return None
    text = content.strip()
    if "{" in text and "}" in text:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            text = text[start : end + 1]
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    functions = []
    for fn in data.get("functions", []) or []:
        if isinstance(fn, dict) and fn.get("name"):
            functions.append(fn)
    data["functions"] = functions
    return data


def fallback_scaffold_spec(idea_line: str, template: str) -> dict[str, Any]:
    """
    Deterministic scaffold packs for offline use (script + fastapi).
    """
    title = strip_idea_prefix(idea_line) or "Kata"
    packs = {
        "script": [
            {
                "title": "String cleanup + counts",
                "summary": "Practice cleaning strings, counting frequencies, and safe arithmetic with tests.",
                "functions": [
                    {
                        "name": "clean_names",
                        "signature": "def clean_names(names: list[str]) -> list[str]",
                        "description": "Trim whitespace, lowercase names, and drop empty values.",
                        "example": {"args": [[" Alice ", "", "BOB"]], "kwargs": {}, "output": ["alice", "bob"]},
                        "edge_cases": ["None or non-iterable input", "Whitespace-only entries", "Mixed casing"],
                    },
                    {
                        "name": "top_counts",
                        "signature": "def top_counts(items: list[str], n: int) -> list[tuple[str, int]]",
                        "description": "Count occurrences and return the top n as (item, count) sorted by count then name.",
                        "example": {"args": [["a", "b", "a", "c", "b", "a"], 2], "kwargs": {}, "output": [["a", 3], ["b", 2]]},
                        "edge_cases": ["n <= 0", "Empty input list", "Ties on count"],
                    },
                    {
                        "name": "safe_divide",
                        "signature": "def safe_divide(a: float, b: float, default=None)",
                        "description": "Divide a by b, returning default on zero division or type errors.",
                        "example": {"args": [10, 2], "kwargs": {"default": None}, "output": 5.0},
                        "edge_cases": ["Zero division", "Non-numeric inputs", "Custom default values"],
                    },
                ],
                "cli": {
                    "description": "Read newline-delimited names from a file and print top 3 counts as JSON.",
                    "example_usage": "python main.py --path names.txt",
                },
            },
            {
                "title": "Mini temperature stats",
                "summary": "Compute min/avg/max temperatures from a list and handle bad inputs cleanly.",
                "functions": [
                    {
                        "name": "parse_temps",
                        "signature": "def parse_temps(raw: list[str]) -> list[float]",
                        "description": "Parse a list of strings into floats, ignoring blanks and invalid tokens.",
                        "example": {"args": [["72.5", "bad", " 68 "]], "kwargs": {}, "output": [72.5, 68.0]},
                        "edge_cases": ["Empty list", "Non-numeric tokens", "Leading/trailing spaces"],
                    },
                    {
                        "name": "summarize_temps",
                        "signature": "def summarize_temps(temps: list[float]) -> dict[str, float]",
                        "description": "Return min, max, and average temperatures rounded to 2 decimals.",
                        "example": {"args": [[72.5, 68.0]], "kwargs": {}, "output": {"min": 68.0, "max": 72.5, "avg": 70.25}},
                        "edge_cases": ["Empty list raises ValueError", "Single element list"],
                    },
                    {
                        "name": "format_report",
                        "signature": "def format_report(summary: dict[str, float]) -> str",
                        "description": "Render a human-readable report line from a summary dict.",
                        "example": {"args": [{"min": 68.0, "max": 72.5, "avg": 70.25}], "kwargs": {}, "output": "Min 68.00, Max 72.50, Avg 70.25"},
                        "edge_cases": ["Missing keys", "Non-numeric values"],
                    },
                ],
                "cli": {
                    "description": "Read temperatures from stdin and print summary.",
                    "example_usage": "echo '72\\n70\\n71' | python main.py",
                },
            },
        ],
        "fastapi": [
            {
                "title": "Echo + stats API",
                "summary": "Expose /health, /echo, and /stats endpoints with validation.",
                "routes": [
                    {
                        "path": "/health",
                        "method": "get",
                        "summary": "Readiness check returning status ok.",
                        "response_example": {"status": "ok"},
                    },
                    {
                        "path": "/echo",
                        "method": "get",
                        "summary": "Echo a query parameter 'message'.",
                        "query_params": {"message": "hi"},
                        "response_example": {"echo": "hi"},
                    },
                    {
                        "path": "/stats",
                        "method": "post",
                        "summary": "Accept list of numbers and return min/max/avg.",
                        "body_example": {"values": [1, 2, 3]},
                        "response_example": {"min": 1, "max": 3, "avg": 2.0},
                    },
                ],
            }
        ],
    }
    chosen_pack = packs.get(template) or packs["script"]
    idx = sum(ord(c) for c in title) % len(chosen_pack)
    pack = chosen_pack[idx]
    pack = dict(pack)
    pack.setdefault("title", title)
    pack["idea"] = idea_line
    pack["summary"] = pack.get("summary") or "Implement the endpoints/functions and make the tests pass."
    return pack


def apply_kata_scaffold(
    target_dir: Path,
    spec: dict[str, Any],
    template: str,
    overwrite_existing: bool = True,
) -> None:
    """
    Materialize kata.md, stubs, and tests from a scaffold spec.
    """
    tests_dir = target_dir / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)
    (tests_dir / "__init__.py").write_text("", encoding="utf-8")

    idea_title = spec.get("title") or "Kata"
    summary = spec.get("summary") or "Implement the functions and make the tests pass."
    functions = spec.get("functions") or []
    routes = spec.get("routes") or []
    if not functions and template == "script":
        functions = fallback_scaffold_spec(spec.get("idea", idea_title), template="script").get("functions", [])
    if not routes and template == "fastapi":
        routes = fallback_scaffold_spec(spec.get("idea", idea_title), template="fastapi").get("routes", [])

    kata_md = target_dir / "kata.md"
    md_lines = [
        f"# {idea_title}",
        "",
        summary,
        "",
        "## Functions to implement",
    ]
    if template == "script":
        for fn in functions:
            md_lines.append(f"- {fn.get('name', 'function')}: {fn.get('description', 'Describe the behavior.')}")
            example = fn.get("example") or {}
            if example:
                md_lines.append(f"  - Example args: {example.get('args', [])}, kwargs: {example.get('kwargs', {})}, output: {example.get('output')}")
            edge = fn.get("edge_cases") or []
            if edge:
                edge_strs = []
                for item in edge:
                    if isinstance(item, dict):
                        if "description" in item:
                            edge_strs.append(str(item.get("description")))
                        else:
                            edge_strs.append(json.dumps(item))
                    else:
                        edge_strs.append(str(item))
                md_lines.append(f"  - Edge cases: {', '.join(edge_strs)}")
    else:
        md_lines.append("Implement the FastAPI routes below:")
        for route in routes:
            md_lines.append(f"- {route.get('method', 'get').upper()} {route.get('path')}: {route.get('summary', '')}")
            if route.get("response_example"):
                md_lines.append(f"  - Response example: {route['response_example']}")
            if route.get("query_params"):
                md_lines.append(f"  - Query params: {route['query_params']}")
            if route.get("body_example"):
                md_lines.append(f"  - Body example: {route['body_example']}")
    md_lines.extend(
        [
            "",
            "## Quickstart",
        ]
    )
    if template == "script":
        md_lines.extend(
            [
                "- Run tests: python -m unittest",
                "- Run script: python main.py",
            ]
        )
    else:
        md_lines.extend(
            [
                "- Run tests: python -m unittest",
                "- Start API: uvicorn main:app --reload",
                "- Hit health: curl http://127.0.0.1:8000/health",
            ]
        )
        md_lines.append("- Start with tests, then fill in stubs.")
    if overwrite_existing or not kata_md.exists():
        kata_md.write_text("\n".join(md_lines), encoding="utf-8")

    main_py = target_dir / "main.py"
    tests_path = tests_dir / "test_main.py"
    if template == "script":
        main_lines = [
            '"""Auto-generated scaffold stubs. Replace with your implementation."""',
            "",
            "def main() -> None:",
            f"    print(\"{idea_title}: implement functions and run tests\")",
            "",
        ]
        for fn in functions:
            signature = (fn.get("signature") or f"def {fn.get('name', 'task')}(*args, **kwargs)").strip()
            if not signature.startswith("def "):
                signature = f"def {signature}"
            if not signature.rstrip().endswith(":"):
                signature = signature.rstrip() + ":"
            desc = summarize_text(fn.get("description", ""), 120)
            main_lines.append(signature)
            if desc:
                main_lines.append(f"    \"\"\"{desc}\"\"\"")
            main_lines.append("    raise NotImplementedError('Implement this function')")
            main_lines.append("")
        if overwrite_existing or not main_py.exists():
            main_py.write_text("\n".join(main_lines), encoding="utf-8")

        fn_names = [fn.get("name", "") for fn in functions if fn.get("name")]
        imports = ", ".join(["main"] + [name for name in fn_names if name])
        test_lines = [
            '"""Auto-generated tests for the scaffold. Edit as needed."""',
            "import unittest",
            f"from main import {imports}  # type: ignore",
            "",
            "class ScaffoldTests(unittest.TestCase):",
            "    def test_main_runs(self) -> None:",
            "        self.assertIsNone(main())",
            "",
        ]
        for fn in functions:
            name = fn.get("name")
            if not name:
                continue
            example = fn.get("example") or {}
            args = _coerce_example_value(example.get("args", []))
            kwargs = _coerce_example_value(example.get("kwargs", {}))
            expected = _coerce_example_value(example.get("output"))
            test_lines.append(f"    def test_{name}_example(self) -> None:")
            test_lines.append(f"        args = {repr(args)}")
            test_lines.append(f"        kwargs = {repr(kwargs)}")
            test_lines.append(f"        result = {name}(*args, **kwargs)")
            if expected is not None:
                test_lines.append(f"        self.assertEqual(result, {repr(expected)})")
            else:
                test_lines.append("        self.fail('Add an expected value for this example')")
            test_lines.append("")
        if overwrite_existing or not tests_path.exists():
            tests_path.write_text("\n".join(test_lines), encoding="utf-8")
    else:
        main_lines = [
            '"""Auto-generated FastAPI scaffold. Fill in route logic."""',
            "from fastapi import FastAPI, HTTPException",
            "from pydantic import BaseModel",
            "",
            f"app = FastAPI(title=\"{idea_title}\")",
            "",
        ]
        needs_payload = any(route.get("body_example") for route in routes)
        if needs_payload:
            main_lines.append("class StatsPayload(BaseModel):")
            main_lines.append("    values: list[float]")
            main_lines.append("")
        for route in routes:
            method = route.get("method", "get").lower()
            path = route.get("path", "/")
            fn_name = route.get("name") or f"{method}_{path.strip('/').replace('/', '_') or 'root'}"
            main_lines.append(f"@app.{method}(\"{path}\")")
            signature = f"def {fn_name}("
            params: list[str] = []
            if route.get("query_params"):
                for key, default in route["query_params"].items():
                    params.append(f"{key}: str")
            if route.get("body_example"):
                params.append("payload: StatsPayload")
            signature += ", ".join(params) + ") -> dict[str, object]:"
            main_lines.append(signature)
            desc = summarize_text(route.get("summary", ""), 120)
            if desc:
                main_lines.append(f"    \"\"\"{desc}\"\"\"")
            main_lines.append("    # TODO: implement route logic")
            main_lines.append("    raise HTTPException(status_code=501, detail=\"Not implemented\")")
            main_lines.append("")
        main_lines.append("")
        main_lines.append("if __name__ == \"__main__\":")
        main_lines.append("    import uvicorn")
        main_lines.append("    uvicorn.run(\"main:app\", host=\"0.0.0.0\", port=8000, reload=True)")
        if overwrite_existing or not main_py.exists():
            main_py.write_text("\n".join(main_lines), encoding="utf-8")

        test_lines = [
            '"""Auto-generated tests for the FastAPI scaffold. Edit as needed."""',
            "import unittest",
            "from fastapi.testclient import TestClient",
            "from main import app",
            "",
            "client = TestClient(app)",
            "",
            "class ScaffoldTests(unittest.TestCase):",
            "    def test_health_exists(self) -> None:",
            "        resp = client.get('/health')",
            "        self.assertEqual(resp.status_code, 200)",
            "        self.assertIsInstance(resp.json(), dict)",
            "",
        ]
        for route in routes:
            path = route.get("path", "/")
            method = route.get("method", "get").lower()
            response_example = route.get("response_example")
            query_params = route.get("query_params") or {}
            body_example = route.get("body_example")
            test_lines.append(f"    def test_{method}_{path.strip('/').replace('/', '_') or 'root'}(self) -> None:")
            if body_example:
                test_lines.append(f"        payload = {repr(body_example)}")
                test_lines.append(f"        resp = client.{method}(\"{path}\", json=payload)")
            else:
                params_repr = repr(query_params)
                if method == "get":
                    test_lines.append(f"        resp = client.get(\"{path}\", params={params_repr})")
                else:
                    test_lines.append(f"        resp = client.{method}(\"{path}\", params={params_repr})")
            test_lines.append("        self.assertEqual(resp.status_code, 200)")
            if response_example is not None:
                test_lines.append("        self.assertEqual(resp.json(), " + repr(response_example) + ")")
            test_lines.append("")
        if overwrite_existing or not tests_path.exists():
            tests_path.write_text("\n".join(test_lines), encoding="utf-8")


def _coerce_example_value(value: Any) -> Any:
    """
    Try to coerce stringified examples into Python values.
    """
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def handle_scaffold_refresh(args: argparse.Namespace) -> int:
    """
    Regenerate missing scaffold files without overwriting user code.
    """
    kata_root = Path(args.root).expanduser()
    project_dir = kata_root / args.project
    if not project_dir.exists():
        print(f"Kata not found at {project_dir}", file=sys.stderr)
        return 1

    idea_title = read_kata_title(project_dir) or args.project
    template = infer_kata_template(project_dir)
    idea_line = f"IDEA: {idea_title} -- scaffold refresh"
    spec = fallback_scaffold_spec(idea_line, template=template)
    apply_kata_scaffold(
        target_dir=project_dir,
        spec=spec,
        template=template,
        overwrite_existing=False,
    )
    print(f"Scaffold refreshed for {args.project} (template={template}). Existing files kept.")
    return 0


def read_kata_title(project_dir: Path) -> str:
    """
    Infer kata title from README first line.
    """
    readme = project_dir / "README.md"
    if not readme.exists():
        return ""
    first_line = readme.read_text().splitlines()
    if not first_line:
        return ""
    line = first_line[0].lstrip("#").strip()
    return line or ""


def infer_kata_template(project_dir: Path) -> str:
    """
    Infer template type from README or files.
    """
    readme = (project_dir / "README.md").read_text() if (project_dir / "README.md").exists() else ""
    if "Template: fastapi" in readme:
        return "fastapi"
    if (project_dir / "requirements.txt").exists() and "fastapi" in (project_dir / "requirements.txt").read_text().lower():
        return "fastapi"
    return "script"


def print_banner() -> None:
    """
    Lightweight ASCII banner for menu mode.
    """
    art = [
        "                                        .___         __        ",
        "  ____   ____ ___  _____ __  ______   __| _/____    |__| ____  ",
        " /    \\_/ __ \\\\  \\/  /  |  \\/  ___/  / __ |/  _ \\   |  |/  _ \\ ",
        "|   |  \\  ___/ >    <|  |  /\\___ \\  / /_/ (  <_> )  |  (  <_> )",
        "|___|  /\\___  >__/\\_ \\____//____  > \\____ |\\____/\\__|  |\\____/ ",
        "     \\/     \\/      \\/          \\/       \\/     \\______|      ",
    ]
    print("\n".join(art))


def seed_test_scaffold(target_dir: Path, template: str, idea_line: str, include_edge: bool) -> None:
    """
    Seed a smoke test (and optional edge-case TODOs) inside the kata.
    """
    tests_dir = target_dir / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)
    (tests_dir / "__init__.py").write_text("")

    idea_title = strip_idea_prefix(idea_line)
    smoke_path = tests_dir / "test_smoke.py"
    if not smoke_path.exists():
        if template == "fastapi":
            smoke_content = (
                '"""Smoke tests for the generated FastAPI app."""\n'
                "import importlib\n"
                "from fastapi import FastAPI\n\n"
                "def test_app_exposes_fastapi_instance() -> None:\n"
                '    module = importlib.import_module("main")\n'
                "    app = getattr(module, \"app\", None)\n"
                "    assert isinstance(app, FastAPI)\n"
            )
        else:
            smoke_content = (
                '"""Smoke tests for the generated script kata."""\n'
                "import importlib\n\n"
                "def test_main_executes() -> None:\n"
                '    module = importlib.import_module("main")\n'
                "    main_fn = getattr(module, \"main\", None)\n"
                "    if callable(main_fn):\n"
                "        main_fn()\n"
            )
        smoke_path.write_text(smoke_content)

    if include_edge:
        edge_path = tests_dir / "test_edge_cases.py"
        if not edge_path.exists():
            edge_content = (
                '"""Edge-case TODOs to harden the kata quickly."""\n'
                "import unittest\n\n"
                f"class EdgeCases(unittest.TestCase):\n"
                f"    @unittest.skip('Fill in edge cases for {idea_title}')\n"
                "    def test_edge_cases(self) -> None:\n"
                "        self.assertTrue(True)\n"
            )
            edge_path.write_text(edge_content)


def main(argv: Optional[Iterable[str]] = None) -> int:
    """
    Entry point for the CLI. Accepts an argv iterable to aid testing.
    """
    parser = build_parser()
    parsed_args = parser.parse_args(list(argv) if argv is not None else None)
    func = getattr(parsed_args, "func", None)
    try:
        if func is None:
            # No command provided: go to menu.
            return handle_menu(argparse.Namespace())
        result = func(parsed_args)
        return int(result) if isinstance(result, int) else 0
    except KeyboardInterrupt:
        console.print("[yellow]Interrupted by user. Exiting.[/yellow]")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
