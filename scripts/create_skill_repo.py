#!/usr/bin/env python3
"""Generate one independent Git repository from the universal Skill runtime template."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def find_official_init() -> Path | None:
    path = Path.home() / ".codex" / "skills" / ".system" / "skill-creator" / "scripts" / "init_skill.py"
    return path if path.is_file() else None


def replace_tokens(text: str, values: dict[str, str]) -> str:
    for token, value in values.items():
        text = text.replace(token, value)
    return text


def destination_for(relative: Path, name: str) -> Path:
    parts = [name if part == "__SKILL_NAME__" else part for part in relative.parts]
    path = Path(*parts)
    if path.name.endswith(".tmpl"):
        path = path.with_name(path.name[:-5])
    return path


def copy_template(template: Path, destination: Path, values: dict[str, str], name: str) -> None:
    for source in sorted(template.rglob("*")):
        if not source.is_file():
            continue
        relative = source.relative_to(template)
        target = destination / destination_for(relative, name)
        target.parent.mkdir(parents=True, exist_ok=True)
        data = source.read_bytes()
        if b"\x00" in data:
            target.write_bytes(data)
            continue
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            target.write_bytes(data)
            continue
        target.write_text(replace_tokens(text, values), encoding="utf-8")


def initialize_official_skill(staging: Path, args: argparse.Namespace) -> str:
    official = None if args.portable else find_official_init()
    if official is None:
        (staging / ".agents" / "skills" / args.name).mkdir(parents=True, exist_ok=True)
        return "portable initializer"
    command = [
        sys.executable,
        str(official),
        args.name,
        "--path",
        str(staging / ".agents" / "skills"),
        "--resources",
        "scripts",
        "--interface",
        f"display_name={args.display_name}",
        "--interface",
        f"short_description={args.short_description}",
        "--interface",
        f"default_prompt={args.default_prompt}",
    ]
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise RuntimeError(f"Official skill initializer failed: {detail}")
    return f"official initializer: {official}"


def run_checked(command: list[str], cwd: Path) -> None:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise RuntimeError(f"Command failed ({' '.join(command)}): {detail}")


def build(args: argparse.Namespace) -> dict[str, str]:
    if not NAME_RE.fullmatch(args.name) or len(args.name) > 64:
        raise RuntimeError("name must be 1-64 lowercase letters, digits, and single hyphens")
    if not 40 <= len(args.description) <= 1024:
        raise RuntimeError("description must be 40-1024 characters")
    if not re.search(r"\bUse (?:this skill )?when\b|用于|当.{0,40}时", args.description, re.I):
        raise RuntimeError("description must state when to use the Skill")
    if not re.search(r"\bDo not use\b|\bnot for\b|不要|不用于|不适用于", args.description, re.I):
        raise RuntimeError("description must state a non-trigger boundary")
    if not 25 <= len(args.short_description) <= 64:
        raise RuntimeError("short-description must be 25-64 characters")
    if f"${args.name}" not in args.default_prompt:
        raise RuntimeError(f"default-prompt must explicitly mention ${args.name}")
    output = args.output.resolve()
    if output.exists():
        raise RuntimeError(f"Refusing to overwrite existing path: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    framework_root = Path(__file__).resolve().parents[1]
    template = framework_root / "template"
    staging = output.parent / f".{output.name}.staging-{uuid.uuid4().hex}"
    staging.mkdir()
    try:
        initializer = initialize_official_skill(staging, args)
        values = {
            "__SKILL_NAME__": args.name,
            "__SKILL_NAME_YAML__": json.dumps(args.name, ensure_ascii=False),
            "__DESCRIPTION_YAML__": json.dumps(args.description, ensure_ascii=False),
            "__DISPLAY_NAME__": args.display_name,
            "__DISPLAY_NAME_YAML__": json.dumps(args.display_name, ensure_ascii=False),
            "__SHORT_DESCRIPTION_YAML__": json.dumps(args.short_description, ensure_ascii=False),
            "__DEFAULT_PROMPT_YAML__": json.dumps(args.default_prompt, ensure_ascii=False),
        }
        copy_template(template, staging, values, args.name)
        for script in staging.rglob("*.py"):
            script.chmod(script.stat().st_mode | 0o111)
        skill_dir = staging / ".agents" / "skills" / args.name
        run_checked([sys.executable, str(skill_dir / "scripts" / "freeze_core.py")], staging)
        run_checked([sys.executable, "scripts/validate.py", "--allow-draft"], staging)
        run_checked(["git", "init", "-b", "main"], staging)
        os.replace(staging, output)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return {"repository": str(output), "skill": args.name, "initializer": initializer}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--description", required=True)
    parser.add_argument("--display-name", required=True)
    parser.add_argument("--short-description", required=True)
    parser.add_argument("--default-prompt", required=True)
    parser.add_argument("--portable", action="store_true")
    args = parser.parse_args()
    try:
        result = build(args)
        print(json.dumps({"created": True, **result}, ensure_ascii=False, indent=2))
        print("The repository is a safe draft. Configure workflow.yaml before the first run.")
        return 0
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
