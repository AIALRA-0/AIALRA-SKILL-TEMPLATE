#!/usr/bin/env python3
"""Validate the universal one-Skill repository template."""

from __future__ import annotations

import argparse
import ast
import re
import sys
import tempfile
from pathlib import Path

from create_skill_repo import build


REQUIRED = (
    "template/AGENTS.md.tmpl",
    "template/.agents/skills/__SKILL_NAME__/SKILL.md.tmpl",
    "template/.agents/skills/__SKILL_NAME__/workflow.yaml.tmpl",
    "template/.agents/skills/__SKILL_NAME__/agents/openai.yaml.tmpl",
    "template/.agents/skills/__SKILL_NAME__/scripts/runner.py",
    "template/.agents/skills/__SKILL_NAME__/scripts/runtime_lib.py",
    "template/.agents/skills/__SKILL_NAME__/scripts/learn.py",
    "template/.agents/skills/__SKILL_NAME__/scripts/compact.py",
    "template/.agents/skills/__SKILL_NAME__/scripts/promote.py",
    "template/.agents/skills/__SKILL_NAME__/scripts/freeze_core.py",
    "template/.agents/skills/__SKILL_NAME__/scripts/validate_repo.py",
    "template/learning/ledger.jsonl",
    "template/learning/active-rules.json",
    "template/tests/test_runtime.py",
)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors: list[str] = []
    for relative in REQUIRED:
        if not (root / relative).is_file():
            errors.append(f"missing template file: {relative}")
    for forbidden in ("catalog", "evals", "templates/profiles"):
        if (root / forbidden).exists():
            errors.append(f"obsolete multi-Skill control plane still exists: {forbidden}")
    if any(path.name == ".git" for path in (root / "template").rglob(".git")):
        errors.append("template must not contain nested Git repositories")
    for path in sorted(root.rglob("*.py")):
        if any(part in {".git", ".venv", "__pycache__"} for part in path.parts):
            continue
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            errors.append(f"Python syntax error in {path.relative_to(root)}:{exc.lineno}: {exc.msg}")
    if not errors:
        with tempfile.TemporaryDirectory(prefix="skill-template-validation-") as temporary:
            output = Path(temporary) / "validate-template-runtime"
            args = argparse.Namespace(
                name="validate-template-runtime",
                output=output,
                description=(
                    "Validate the generated graph-driven Skill repository. Use when testing the universal "
                    "template output. Do not use for production work or unrelated repository validation."
                ),
                display_name="Validate Template Runtime",
                short_description="Validate a generated graph-driven Skill",
                default_prompt=(
                    "Use $validate-template-runtime to validate this generated template repository."
                ),
                portable=True,
            )
            try:
                build(args)
            except (OSError, RuntimeError) as exc:
                errors.append(f"template generation failed: {exc}")
            else:
                if not (output / ".git").is_dir():
                    errors.append("generated repository is missing its independent .git directory")
                placeholder = re.compile(r"__[A-Z][A-Z0-9_]*__")
                for generated in sorted(output.rglob("*")):
                    if not generated.is_file() or ".git" in generated.parts:
                        continue
                    try:
                        text = generated.read_text(encoding="utf-8")
                    except UnicodeDecodeError:
                        continue
                    match = placeholder.search(text)
                    if match:
                        errors.append(
                            f"generated repository contains unresolved token {match.group(0)} in "
                            f"{generated.relative_to(output)}"
                        )
    if errors:
        print(f"Template validation failed with {len(errors)} error(s):", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Universal one-Skill repository template is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
