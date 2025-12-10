"""
Command-line interface for the NexusDojo scaffold.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, Optional

from . import __version__

# Default workspace location for local knowledge artifacts.
DEFAULT_WORKSPACE = Path("./nexusdojo_data")
# Default root for dojo katas.
DEFAULT_KATA_ROOT = Path("./dojo")
# Default root for notes and briefs.
DEFAULT_NOTES_ROOT = Path("./notes")
# Location of bundled templates (relative to repo root).
TEMPLATES_ROOT = Path(__file__).resolve().parents[2] / "templates"
# Default model settings for idea generation.
DEFAULT_IDEA_PROVIDER = "ollama"
DEFAULT_IDEA_MODEL = "llama3.2:1b"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"


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
        choices=["script", "fastapi"],
        help="Template to use for the new kata (default: script).",
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
    start_parser.set_defaults(func=handle_start)

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

    # Friendly menu when no command is provided.
    menu_parser = subparsers.add_parser(
        "menu",
        help="Interactive menu for common tasks.",
    )
    menu_parser.set_defaults(func=handle_menu)

    return parser


def handle_hello(_: argparse.Namespace) -> int:
    """
    Print a short quickstart message.
    """
    print("Welcome to the NexusDojo CLI scaffold.")
    print("Next steps: `dojo init` to create a workspace, then wire ingestion/search.")
    return 0


def handle_info(_: argparse.Namespace) -> int:
    """
    Display environment information useful for debugging.
    """
    print(f"NexusDojo CLI v{__version__}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Platform: {platform.platform()}")
    print(f"Working directory: {Path.cwd()}")
    print(f"Default workspace: {DEFAULT_WORKSPACE}")
    print(f"Default kata root: {DEFAULT_KATA_ROOT}")
    print(f"Default notes root: {DEFAULT_NOTES_ROOT}")
    return 0


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
    if not idea:
        print("No idea provided; using idea picker...", file=sys.stderr)
        picked = pick_idea(
            provider=DEFAULT_IDEA_PROVIDER,
            model=DEFAULT_IDEA_MODEL,
            kata_root=Path(args.root).expanduser(),
            notes_root=Path(args.notes_root).expanduser(),
        )
        if not picked:
            print("Idea picker failed; please provide an idea manually.", file=sys.stderr)
            return 1
        idea = picked
        print(f"Using idea: {idea}")

    slug = slugify(idea)
    if not slug:
        print("Idea is empty after slugifying; provide a short description.", file=sys.stderr)
        return 1

    kata_root = Path(args.root).expanduser()
    kata_root.mkdir(parents=True, exist_ok=True)
    target_dir = kata_root / slug

    if target_dir.exists() and any(target_dir.iterdir()) and not args.force:
        print(
            f"Kata directory {target_dir} exists and is not empty. Use --force to reuse it.",
            file=sys.stderr,
        )
        return 1

    template_dir = TEMPLATES_ROOT / args.template
    if not template_dir.exists():
        print(f"Template not found: {template_dir}", file=sys.stderr)
        return 1

    shutil.copytree(template_dir, target_dir, dirs_exist_ok=args.force)

    replacements = {
        "IDEA": idea,
        "SLUG": slug,
        "TEMPLATE": args.template,
        "CREATED_AT": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    readme_path = target_dir / "README.md"
    if readme_path.exists():
        apply_placeholders(readme_path, replacements)

    print(f"Created kata at {target_dir}")
    return 0


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


def handle_menu(_: argparse.Namespace) -> int:
    """
    Simple interactive menu for common tasks.
    """
    options = [
        ("Start a kata (auto idea)", "start_auto"),
        ("Get ideas only", "idea"),
        ("Log progress", "log"),
        ("Show a brief", "brief"),
        ("Show info", "info"),
        ("Exit", "exit"),
    ]
    print("NexusDojo menu:")
    for idx, (label, _) in enumerate(options, start=1):
        print(f"{idx}) {label}")
    choice = input("Select an option: ").strip()
    try:
        idx = int(choice)
    except ValueError:
        print("Invalid choice.")
        return 1
    if idx < 1 or idx > len(options):
        print("Invalid choice.")
        return 1
    action = options[idx - 1][1]
    if action == "exit":
        return 0
    if action == "info":
        return handle_info(argparse.Namespace())
    if action == "idea":
        return handle_idea(
            argparse.Namespace(
                provider=DEFAULT_IDEA_PROVIDER,
                model=DEFAULT_IDEA_MODEL,
                root=str(DEFAULT_KATA_ROOT),
                notes_root=str(DEFAULT_NOTES_ROOT),
                dry_run=False,
            )
        )
    if action == "brief":
        return handle_brief(
            argparse.Namespace(
                since=None,
                root=str(DEFAULT_KATA_ROOT),
                notes_root=str(DEFAULT_NOTES_ROOT),
            )
        )
    if action == "log":
        project = input("Kata slug: ").strip()
        note = input("Note: ").strip()
        return handle_log(
            argparse.Namespace(
                project=project,
                note=note,
                root=str(DEFAULT_KATA_ROOT),
                notes_root=str(DEFAULT_NOTES_ROOT),
            )
        )
    if action == "start_auto":
        pillar = input("Focus pillar (python/cli/api/testing/mixed) [mixed]: ").strip().lower() or "mixed"
        if pillar not in {"python", "cli", "api", "testing", "mixed"}:
            pillar = "mixed"
        mode = input("Mode/template (script/api) [script]: ").strip().lower() or "script"
        if mode not in {"script", "api"}:
            mode = "script"
        template = "fastapi" if mode == "api" else "script"
        level = input("Difficulty (foundation/proficient/stretch) [foundation]: ").strip().lower() or "foundation"
        if level not in {"foundation", "proficient", "stretch"}:
            level = "foundation"

        idea = pick_idea_with_hints(
            provider=DEFAULT_IDEA_PROVIDER,
            model=DEFAULT_IDEA_MODEL,
            kata_root=Path(DEFAULT_KATA_ROOT),
            notes_root=Path(DEFAULT_NOTES_ROOT),
            pillar_hint=pillar,
            level_hint=level,
            mode_hint=mode,
        )
        if not idea:
            print("Could not generate an idea. Try again.")
            return 1

        print("\nProposed kata:")
        print(f"- Focus: {pillar} | Mode: {mode} ({template}) | Level: {level}")
        print(f"- Idea: {idea}")
        confirm = input("Create this kata? (y/n): ").strip().lower()
        if confirm != "y":
            print("Canceled.")
            return 0

        return handle_start(
            argparse.Namespace(
                idea=idea,
                template=template,
                root=str(DEFAULT_KATA_ROOT),
                notes_root=str(DEFAULT_NOTES_ROOT),
                force=False,
            )
        )
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

    idea = call_idea_api(
        provider=args.provider,
        model=args.model,
        messages=messages,
    )
    if not idea:
        print("Idea generation failed. Check your API key and network.", file=sys.stderr)
        return 1

    print(f"Weakest pillar (from calibrations): {weakest or 'unknown'}")
    print("Suggested ideas:")
    print(idea)
    return 0


def append_line(path: Path, line: str) -> None:
    """
    Append a line to a file, creating the file if needed.
    """
    with path.open("a", encoding="utf-8") as handle:
        handle.write(line)


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

    system = (
        "You are the NexusDojo idea picker. Return ONE idea only in this exact format:\n"
        "IDEA: <short title> -- <1 sentence spec>\n"
        "Keep it runnable in under a few hours. No prefacing text. No extra bullets."
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
            with urllib.request.urlopen(request, timeout=30) as resp:
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
            with urllib.request.urlopen(request, timeout=30) as resp:
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
) -> Optional[str]:
    """
    Generate an idea using hints; fall back to canned ideas if needed.
    """
    messages, _ = build_idea_prompt(
        kata_root=kata_root,
        notes_root=notes_root,
        pillar_hint=pillar_hint,
        level_hint=level_hint,
        mode_hint=mode_hint,
    )
    content = call_idea_api(provider=provider, model=model, messages=messages)
    idea = parse_idea_content(content) if content else None
    if idea:
        return idea
    return fallback_idea(pillar_hint=pillar_hint, level_hint=level_hint, mode_hint=mode_hint)


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
            return cleaned.replace("IDEA:", "", 1).strip()
        if cleaned.startswith(("-", "*", "•")):
            cleaned = cleaned.lstrip("-*• ").strip()
        if cleaned:
            return cleaned
    return None


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
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug


def main(argv: Optional[Iterable[str]] = None) -> int:
    """
    Entry point for the CLI. Accepts an argv iterable to aid testing.
    """
    parser = build_parser()
    parsed_args = parser.parse_args(list(argv) if argv is not None else None)
    func = getattr(parsed_args, "func", None)
    if func is None:
        # No command provided: go to menu.
        return handle_menu(argparse.Namespace())
    result = func(parsed_args)
    return int(result) if isinstance(result, int) else 0


if __name__ == "__main__":
    raise SystemExit(main())
