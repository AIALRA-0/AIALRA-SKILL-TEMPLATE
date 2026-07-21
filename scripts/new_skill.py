#!/usr/bin/env python3
"""Create or update a catalog-driven Codex Skill."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from skill_framework import (
    canonical_spec,
    load_spec,
    render_openai_yaml,
    render_skill,
    render_task_cases,
    render_trigger_queries,
    repo_root,
    validate_spec,
)


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def find_official_init() -> Path | None:
    candidate = Path.home() / ".codex" / "skills" / ".system" / "skill-creator" / "scripts" / "init_skill.py"
    return candidate if candidate.is_file() else None


def initialize_skill_dir(
    skill_dir: Path, spec: dict, use_official: bool
) -> str:
    resource_names = [
        name for name in ("scripts", "references", "assets") if spec["resources"][name]
    ]
    official = find_official_init() if use_official else None
    if official:
        with tempfile.TemporaryDirectory(prefix="skill-framework-init-") as temporary:
            command = [
                sys.executable,
                str(official),
                spec["name"],
                "--path",
                temporary,
                "--interface",
                f'display_name={spec["interface"]["display_name"]}',
                "--interface",
                f'short_description={spec["interface"]["short_description"]}',
                "--interface",
                f'default_prompt={spec["interface"]["default_prompt"]}',
            ]
            if resource_names:
                command.extend(["--resources", ",".join(resource_names)])
            result = subprocess.run(command, text=True, capture_output=True, check=False)
            if result.returncode != 0:
                detail = (result.stderr or result.stdout).strip()
                raise RuntimeError(f"Official skill initializer failed: {detail}")
            shutil.copytree(Path(temporary) / spec["name"], skill_dir)
        return f"official initializer: {official}"

    skill_dir.mkdir(parents=True, exist_ok=False)
    (skill_dir / "agents").mkdir()
    for resource_name in resource_names:
        (skill_dir / resource_name).mkdir()
    return "portable initializer"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, type=Path, help="Path to a Skill design spec JSON file")
    parser.add_argument("--update", action="store_true", help="Regenerate an existing Skill")
    parser.add_argument(
        "--portable",
        action="store_true",
        help="Skip the local official skill-creator initializer (useful in CI/tests)",
    )
    args = parser.parse_args()
    root = repo_root()
    try:
        spec = load_spec(args.spec.resolve())
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    errors = validate_spec(spec)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 2

    name = spec["name"]
    skill_dir = root / ".agents" / "skills" / name
    catalog_file = root / "catalog" / f"{name}.json"
    eval_dir = root / "evals" / name
    initializer = "update"
    if args.update:
        if not skill_dir.is_dir() or not catalog_file.is_file():
            print(f"ERROR: cannot update missing Skill {name}", file=sys.stderr)
            return 2
    else:
        occupied = [path for path in (skill_dir, catalog_file, eval_dir) if path.exists()]
        if occupied:
            print(
                "ERROR: refusing to overwrite existing paths: "
                + ", ".join(str(path.relative_to(root)) for path in occupied),
                file=sys.stderr,
            )
            return 2
        try:
            initializer = initialize_skill_dir(skill_dir, spec, use_official=not args.portable)
        except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2

    try:
        for category in ("references", "scripts", "assets"):
            if spec["resources"][category]:
                (skill_dir / category).mkdir(parents=True, exist_ok=True)
        atomic_write(skill_dir / "SKILL.md", render_skill(spec, root))
        atomic_write(skill_dir / "agents" / "openai.yaml", render_openai_yaml(spec))
        atomic_write(catalog_file, canonical_spec(spec))
        atomic_write(eval_dir / "trigger_queries.json", render_trigger_queries(spec))
        atomic_write(eval_dir / "task_cases.json", render_task_cases(spec))
    except (OSError, KeyError, ValueError) as exc:
        print(f"ERROR: generation failed: {exc}", file=sys.stderr)
        return 2

    missing_resources: list[str] = []
    for category in ("references", "scripts", "assets"):
        for item in spec["resources"][category]:
            if not (skill_dir / item["path"]).is_file():
                missing_resources.append(item["path"])
    print(f"Generated {name} using {initializer}.")
    if missing_resources:
        print("Add the declared resource files before repository validation:")
        for path in missing_resources:
            print(f"  - .agents/skills/{name}/{path}")
    else:
        print("All declared resources are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
