#!/usr/bin/env python3
"""Validate catalog entries and deterministic generated Skill artifacts."""

from __future__ import annotations

import sys
from pathlib import Path

from skill_framework import load_spec, repo_root, validate_skill_against_spec


def main() -> int:
    root = repo_root()
    catalog_dir = root / "catalog"
    skill_root = root / ".agents" / "skills"
    eval_root = root / "evals"
    catalog_files = sorted(catalog_dir.glob("*.json")) if catalog_dir.is_dir() else []
    errors: list[str] = []
    catalog_names: set[str] = set()
    for catalog_file in catalog_files:
        try:
            spec = load_spec(catalog_file)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        name = spec.get("name")
        if isinstance(name, str):
            catalog_names.add(name)
            if catalog_file.stem != name:
                errors.append(f"catalog filename must match name: {catalog_file.name} != {name}.json")
        for error in validate_skill_against_spec(root, spec):
            errors.append(f"{catalog_file.relative_to(root)}: {error}")

    skill_names = {path.name for path in skill_root.iterdir() if path.is_dir()} if skill_root.is_dir() else set()
    eval_names = {path.name for path in eval_root.iterdir() if path.is_dir()} if eval_root.is_dir() else set()
    for name in sorted(skill_names - catalog_names):
        errors.append(f"runtime Skill has no catalog entry: .agents/skills/{name}")
    for name in sorted(eval_names - catalog_names):
        errors.append(f"eval directory has no catalog entry: evals/{name}")
    for name in sorted(catalog_names - skill_names):
        errors.append(f"catalog entry has no runtime Skill: catalog/{name}.json")

    if errors:
        print(f"Validation failed with {len(errors)} error(s):", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Validated {len(catalog_files)} catalog-driven Skill(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
