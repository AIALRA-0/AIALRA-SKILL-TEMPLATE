#!/usr/bin/env python3
"""Core rendering and validation for the Skill framework."""

from __future__ import annotations

import datetime as dt
import json
import math
import re
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER_RE = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$"
)
PLACEHOLDER_RE = re.compile(r"\[\[REQUIRED:|\{\{[A-Z0-9_]+\}\}|\bREPLACE_ME\b|\bTODO\b")
PROFILES = {
    "research": {
        "source_priority": list,
        "freshness_rule": str,
        "evidence_fields": list,
        "conflict_rule": str,
        "coverage_rule": str,
    },
    "tool-integration": {
        "capabilities": list,
        "auth_boundary": str,
        "read_actions": list,
        "write_actions": list,
        "confirmation_points": list,
        "fallbacks": list,
        "failure_handling": str,
    },
    "artifact-production": {
        "input_inspection": list,
        "production_method": str,
        "render_or_run": list,
        "handoff_standard": str,
        "quality_checks": list,
    },
    "operational-workflow": {
        "preconditions": list,
        "stage_gates": list,
        "rollback": list,
        "completion_criteria": list,
    },
}
FORBIDDEN_SKILL_DOCS = {
    "README.md",
    "CHANGELOG.md",
    "INSTALLATION_GUIDE.md",
    "QUICK_REFERENCE.md",
    "CONTRIBUTING.md",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_spec(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Spec not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"Spec root must be an object: {path}")
    return data


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _check_string_list(
    errors: list[str], value: Any, field: str, minimum: int = 1
) -> None:
    if not isinstance(value, list) or len(value) < minimum:
        errors.append(f"{field} must contain at least {minimum} item(s)")
        return
    for index, item in enumerate(value):
        if not _is_nonempty_string(item):
            errors.append(f"{field}[{index}] must be a non-empty string")


def _safe_resource_path(path: Any, category: str) -> bool:
    if not _is_nonempty_string(path):
        return False
    pure = PurePosixPath(path)
    expected_prefix = {"references": "references", "scripts": "scripts", "assets": "assets"}[category]
    return (
        not pure.is_absolute()
        and ".." not in pure.parts
        and len(pure.parts) >= 2
        and pure.parts[0] == expected_prefix
    )


def validate_spec(
    spec: dict[str, Any], root: Path | None = None, check_resources: bool = False
) -> list[str]:
    errors: list[str] = []
    required = {
        "schema_version",
        "name",
        "profile",
        "description",
        "interface",
        "contract",
        "workflow",
        "guardrails",
        "gotchas",
        "verification",
        "profile_fields",
        "resources",
        "dependencies",
        "maintenance",
        "evaluation",
        "triggers",
        "evals",
    }
    allowed = required | {"$schema"}
    missing = sorted(required - set(spec))
    if missing:
        errors.append(f"missing required fields: {', '.join(missing)}")
    unknown = sorted(set(spec) - allowed)
    if unknown:
        errors.append(f"unsupported top-level fields: {', '.join(unknown)}")
    if spec.get("schema_version") != "1.0":
        errors.append("schema_version must be '1.0'")

    name = spec.get("name")
    if not _is_nonempty_string(name) or not NAME_RE.fullmatch(name) or len(name) > 64:
        errors.append("name must be 1-64 lowercase letters, digits, and single hyphens")

    profile = spec.get("profile")
    if profile not in PROFILES:
        errors.append(f"profile must be one of: {', '.join(PROFILES)}")

    description = spec.get("description")
    if not _is_nonempty_string(description) or not 40 <= len(description) <= 1024:
        errors.append("description must be 40-1024 characters")
    elif not re.search(r"\bUse (?:this skill )?when\b|用于|当.{0,40}时", description, re.IGNORECASE):
        errors.append("description must state when to use the skill")
    elif not re.search(r"\bDo not use\b|\bnot for\b|不要|不用于|不适用于", description, re.IGNORECASE):
        errors.append("description must state a non-trigger boundary")

    interface = spec.get("interface")
    if not isinstance(interface, dict):
        errors.append("interface must be an object")
        interface = {}
    else:
        extra = sorted(
            set(interface)
            - {"display_name", "short_description", "default_prompt", "allow_implicit_invocation"}
        )
        if extra:
            errors.append(f"interface contains unsupported fields: {', '.join(extra)}")
    for field in ("display_name", "short_description", "default_prompt"):
        if not _is_nonempty_string(interface.get(field)):
            errors.append(f"interface.{field} must be a non-empty string")
    short_description = interface.get("short_description", "")
    if isinstance(short_description, str) and not 25 <= len(short_description) <= 64:
        errors.append("interface.short_description must be 25-64 characters")
    default_prompt = interface.get("default_prompt", "")
    if _is_nonempty_string(name) and _is_nonempty_string(default_prompt) and f"${name}" not in default_prompt:
        errors.append(f"interface.default_prompt must explicitly mention ${name}")
    if not isinstance(interface.get("allow_implicit_invocation"), bool):
        errors.append("interface.allow_implicit_invocation must be boolean")

    contract = spec.get("contract")
    if not isinstance(contract, dict):
        errors.append("contract must be an object")
        contract = {}
    else:
        extra = sorted(set(contract) - {"goal", "inputs", "outputs", "non_goals"})
        if extra:
            errors.append(f"contract contains unsupported fields: {', '.join(extra)}")
    if not _is_nonempty_string(contract.get("goal")):
        errors.append("contract.goal must be a non-empty string")
    for field in ("inputs", "outputs", "non_goals"):
        _check_string_list(errors, contract.get(field), f"contract.{field}")

    _check_string_list(errors, spec.get("workflow"), "workflow", minimum=3)
    _check_string_list(errors, spec.get("guardrails"), "guardrails")
    _check_string_list(errors, spec.get("gotchas"), "gotchas")
    _check_string_list(errors, spec.get("verification"), "verification")

    profile_fields = spec.get("profile_fields")
    if not isinstance(profile_fields, dict):
        errors.append("profile_fields must be an object")
        profile_fields = {}
    if profile in PROFILES:
        expected = PROFILES[profile]
        unknown = sorted(set(profile_fields) - set(expected))
        if unknown:
            errors.append(f"profile_fields contains unsupported fields for {profile}: {', '.join(unknown)}")
        for field, expected_type in expected.items():
            value = profile_fields.get(field)
            if expected_type is list:
                _check_string_list(errors, value, f"profile_fields.{field}")
            elif not _is_nonempty_string(value):
                errors.append(f"profile_fields.{field} must be a non-empty string")

    resources = spec.get("resources")
    if not isinstance(resources, dict):
        errors.append("resources must be an object")
        resources = {}
    else:
        extra = sorted(set(resources) - {"references", "scripts", "assets"})
        if extra:
            errors.append(f"resources contains unsupported fields: {', '.join(extra)}")
    for category in ("references", "scripts", "assets"):
        entries = resources.get(category)
        if not isinstance(entries, list):
            errors.append(f"resources.{category} must be an array")
            continue
        seen_paths: set[str] = set()
        for index, item in enumerate(entries):
            field = f"resources.{category}[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{field} must be an object")
                continue
            path = item.get("path")
            if not _safe_resource_path(path, category):
                errors.append(f"{field}.path must be a safe relative path under {category}/")
            elif path in seen_paths:
                errors.append(f"duplicate resource path: {path}")
            else:
                seen_paths.add(path)
                if check_resources and root is not None and _is_nonempty_string(name):
                    skill_path = root / ".agents" / "skills" / name / path
                    if not skill_path.is_file():
                        errors.append(f"declared resource does not exist: {skill_path.relative_to(root)}")
            for key in ("purpose", "load_when"):
                if not _is_nonempty_string(item.get(key)):
                    errors.append(f"{field}.{key} must be a non-empty string")

    dependencies = spec.get("dependencies")
    if not isinstance(dependencies, dict) or not isinstance(dependencies.get("mcp"), list):
        errors.append("dependencies.mcp must be an array")
    else:
        extra = sorted(set(dependencies) - {"mcp"})
        if extra:
            errors.append(f"dependencies contains unsupported fields: {', '.join(extra)}")
        for index, item in enumerate(dependencies["mcp"]):
            field = f"dependencies.mcp[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{field} must be an object")
                continue
            for key in ("value", "description", "transport", "url"):
                if not _is_nonempty_string(item.get(key)):
                    errors.append(f"{field}.{key} must be a non-empty string")
            if _is_nonempty_string(item.get("url")) and not item["url"].startswith("https://"):
                errors.append(f"{field}.url must use https")

    maintenance = spec.get("maintenance")
    if not isinstance(maintenance, dict):
        errors.append("maintenance must be an object")
        maintenance = {}
    else:
        extra = sorted(
            set(maintenance)
            - {"owner", "version", "status", "last_reviewed", "review_interval_days", "risk"}
        )
        if extra:
            errors.append(f"maintenance contains unsupported fields: {', '.join(extra)}")
    if not _is_nonempty_string(maintenance.get("owner")):
        errors.append("maintenance.owner must be a non-empty role or handle")
    if not _is_nonempty_string(maintenance.get("version")) or not SEMVER_RE.fullmatch(
        maintenance.get("version", "")
    ):
        errors.append("maintenance.version must be valid SemVer")
    status = maintenance.get("status")
    if status not in {"draft", "candidate", "stable", "deprecated"}:
        errors.append("maintenance.status is invalid")
    try:
        dt.date.fromisoformat(maintenance.get("last_reviewed", ""))
    except (TypeError, ValueError):
        errors.append("maintenance.last_reviewed must be an ISO date")
    review_days = maintenance.get("review_interval_days")
    if not isinstance(review_days, int) or not 1 <= review_days <= 365:
        errors.append("maintenance.review_interval_days must be 1-365")
    if maintenance.get("risk") not in {"low", "medium", "high"}:
        errors.append("maintenance.risk must be low, medium, or high")

    evaluation = spec.get("evaluation")
    if not isinstance(evaluation, dict):
        errors.append("evaluation must be an object")
        evaluation = {}
    else:
        extra = sorted(
            set(evaluation)
            - {"routing_runs_per_query", "baseline", "last_run", "summary"}
        )
        if extra:
            errors.append(f"evaluation contains unsupported fields: {', '.join(extra)}")
    routing_runs = evaluation.get("routing_runs_per_query")
    if not isinstance(routing_runs, int) or not 1 <= routing_runs <= 20:
        errors.append("evaluation.routing_runs_per_query must be 1-20")
    baseline = evaluation.get("baseline")
    if baseline not in {"not-run", "no-skill", "previous-version"}:
        errors.append("evaluation.baseline is invalid")
    last_run = evaluation.get("last_run")
    if last_run is not None:
        try:
            dt.date.fromisoformat(last_run)
        except (TypeError, ValueError):
            errors.append("evaluation.last_run must be null or an ISO date")
    if not _is_nonempty_string(evaluation.get("summary")):
        errors.append("evaluation.summary must be a non-empty string")
    if status in {"candidate", "stable"}:
        if baseline == "not-run" or last_run is None:
            errors.append("candidate and stable Skills require completed baseline evaluation metadata")
        if isinstance(routing_runs, int) and routing_runs < 3:
            errors.append("candidate and stable Skills require at least 3 routing runs per query")

    triggers = spec.get("triggers")
    if not isinstance(triggers, dict):
        errors.append("triggers must be an object")
        triggers = {}
    minimum = 8 if status in {"candidate", "stable"} else 3
    for label in ("positive", "negative"):
        _check_string_list(errors, triggers.get(label), f"triggers.{label}", minimum=minimum)
        values = triggers.get(label)
        if isinstance(values, list) and len(values) != len(set(values)):
            errors.append(f"triggers.{label} contains duplicates")
    positives = set(triggers.get("positive", [])) if isinstance(triggers.get("positive"), list) else set()
    negatives = set(triggers.get("negative", [])) if isinstance(triggers.get("negative"), list) else set()
    if positives & negatives:
        errors.append("the same query cannot be both a positive and negative trigger")

    evals = spec.get("evals")
    required_evals = 2 if status in {"candidate", "stable"} else 1
    if not isinstance(evals, list) or len(evals) < required_evals:
        errors.append(f"evals must contain at least {required_evals} task case(s)")
    else:
        seen_ids: set[str] = set()
        for index, case in enumerate(evals):
            field = f"evals[{index}]"
            if not isinstance(case, dict):
                errors.append(f"{field} must be an object")
                continue
            case_id = case.get("id")
            if not _is_nonempty_string(case_id) or not NAME_RE.fullmatch(case_id):
                errors.append(f"{field}.id must use lowercase kebab-case")
            elif case_id in seen_ids:
                errors.append(f"duplicate eval id: {case_id}")
            else:
                seen_ids.add(case_id)
            for key in ("prompt", "expected_output"):
                if not _is_nonempty_string(case.get(key)):
                    errors.append(f"{field}.{key} must be a non-empty string")
            _check_string_list(errors, case.get("assertions"), f"{field}.assertions")
            if "files" in case and not isinstance(case["files"], list):
                errors.append(f"{field}.files must be an array")

    serialized = json.dumps(spec, ensure_ascii=False)
    if PLACEHOLDER_RE.search(serialized):
        errors.append("spec contains unresolved TODO/template placeholders")
    return errors


def yaml_quote(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def bullets(items: Iterable[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def numbered(items: Iterable[str]) -> str:
    return "\n".join(f"{index}. {item}" for index, item in enumerate(items, start=1))


def render_resources(spec: dict[str, Any]) -> str:
    lines: list[str] = []
    labels = {"references": "Reference", "scripts": "Script", "assets": "Asset"}
    for category in ("references", "scripts", "assets"):
        for item in spec["resources"][category]:
            lines.append(
                f'- {labels[category]} [{item["path"]}]({item["path"]}) — '
                f'{item["purpose"]} Load when: {item["load_when"]}'
            )
    for item in spec["dependencies"]["mcp"]:
        lines.append(
            f'- MCP `{item["value"]}` — {item["description"]} '
            f'({item["transport"]}, {item["url"]})'
        )
    return "\n".join(lines) if lines else "No bundled resources or MCP dependencies are required."


def render_skill(spec: dict[str, Any], root: Path | None = None) -> str:
    root = root or repo_root()
    profile = spec["profile"]
    template_path = root / "templates" / "profiles" / f"{profile}.md.tmpl"
    template = template_path.read_text(encoding="utf-8")
    contract = spec["contract"]
    profile_fields = spec["profile_fields"]
    values: dict[str, str] = {
        "NAME_YAML": yaml_quote(spec["name"]),
        "DESCRIPTION_YAML": yaml_quote(spec["description"]),
        "DISPLAY_NAME": spec["interface"]["display_name"],
        "GOAL": contract["goal"],
        "INPUTS": bullets(contract["inputs"]),
        "OUTPUTS": bullets(contract["outputs"]),
        "NON_GOALS": bullets(contract["non_goals"]),
        "WORKFLOW": numbered(spec["workflow"]),
        "GUARDRAILS": bullets(spec["guardrails"]),
        "GOTCHAS": bullets(spec["gotchas"]),
        "VERIFICATION": bullets(spec["verification"]),
        "RESOURCES": render_resources(spec),
    }
    for key, value in profile_fields.items():
        values[key.upper()] = bullets(value) if isinstance(value, list) else value
    rendered = template
    for key, value in values.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    unresolved = sorted(set(re.findall(r"\{\{([A-Z0-9_]+)\}\}", rendered)))
    if unresolved:
        raise ValueError(f"Template has unresolved fields: {', '.join(unresolved)}")
    return rendered.rstrip() + "\n"


def render_openai_yaml(spec: dict[str, Any]) -> str:
    interface = spec["interface"]
    lines = [
        "interface:",
        f'  display_name: {yaml_quote(interface["display_name"])}',
        f'  short_description: {yaml_quote(interface["short_description"])}',
        f'  default_prompt: {yaml_quote(interface["default_prompt"])}',
    ]
    mcp_dependencies = spec["dependencies"]["mcp"]
    if mcp_dependencies:
        lines.extend(["", "dependencies:", "  tools:"])
        for item in mcp_dependencies:
            lines.extend(
                [
                    '    - type: "mcp"',
                    f'      value: {yaml_quote(item["value"])}',
                    f'      description: {yaml_quote(item["description"])}',
                    f'      transport: {yaml_quote(item["transport"])}',
                    f'      url: {yaml_quote(item["url"])}',
                ]
            )
    implicit = "true" if interface["allow_implicit_invocation"] else "false"
    lines.extend(["", "policy:", f"  allow_implicit_invocation: {implicit}"])
    return "\n".join(lines) + "\n"


def _split_label(index: int, total: int) -> str:
    train_count = max(1, math.ceil(total * 0.6))
    return "train" if index < train_count else "validation"


def render_trigger_queries(spec: dict[str, Any]) -> str:
    rows: list[dict[str, Any]] = []
    for should_trigger, label in ((True, "positive"), (False, "negative")):
        queries = spec["triggers"][label]
        for index, query in enumerate(queries):
            rows.append(
                {
                    "query": query,
                    "should_trigger": should_trigger,
                    "split": _split_label(index, len(queries)),
                }
            )
    return json.dumps(rows, indent=2, ensure_ascii=False) + "\n"


def render_task_cases(spec: dict[str, Any]) -> str:
    payload = {
        "skill_name": spec["name"],
        "skill_version": spec["maintenance"]["version"],
        "evaluation": spec["evaluation"],
        "evals": spec["evals"],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def canonical_spec(spec: dict[str, Any]) -> str:
    return json.dumps(spec, indent=2, ensure_ascii=False) + "\n"


def parse_frontmatter(skill_text: str) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = []
    lines = skill_text.splitlines()
    if len(lines) < 4 or lines[0].strip() != "---":
        return {}, ["SKILL.md must start with YAML frontmatter"]
    try:
        closing = lines.index("---", 1)
    except ValueError:
        return {}, ["SKILL.md frontmatter is not closed"]
    fields: dict[str, str] = {}
    for index, line in enumerate(lines[1:closing], start=2):
        if not line.strip():
            continue
        if ":" not in line:
            errors.append(f"invalid frontmatter line {index}")
            continue
        key, raw = line.split(":", 1)
        key = key.strip()
        raw = raw.strip()
        try:
            value = json.loads(raw) if raw.startswith(('"', "'")) else raw
        except json.JSONDecodeError:
            value = raw.strip('"')
        fields[key] = value
    return fields, errors


def validate_skill_against_spec(root: Path, spec: dict[str, Any]) -> list[str]:
    errors = validate_spec(spec, root=root, check_resources=True)
    name = spec.get("name", "invalid")
    skill_dir = root / ".agents" / "skills" / name
    skill_file = skill_dir / "SKILL.md"
    yaml_file = skill_dir / "agents" / "openai.yaml"
    trigger_file = root / "evals" / name / "trigger_queries.json"
    task_file = root / "evals" / name / "task_cases.json"
    expected_files = {
        skill_file: lambda: render_skill(spec, root),
        yaml_file: lambda: render_openai_yaml(spec),
        trigger_file: lambda: render_trigger_queries(spec),
        task_file: lambda: render_task_cases(spec),
    }
    for path, renderer in expected_files.items():
        if not path.is_file():
            errors.append(f"generated file missing: {path.relative_to(root)}")
            continue
        actual = path.read_text(encoding="utf-8")
        try:
            expected = renderer()
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"cannot render {path.relative_to(root)}: {exc}")
            continue
        if actual != expected:
            errors.append(f"generated file drift: {path.relative_to(root)}; run new_skill.py --update")

    if skill_file.is_file():
        skill_text = skill_file.read_text(encoding="utf-8")
        fields, frontmatter_errors = parse_frontmatter(skill_text)
        errors.extend(frontmatter_errors)
        if set(fields) != {"name", "description"}:
            errors.append(f"{skill_file.relative_to(root)} frontmatter must contain only name and description")
        if fields.get("name") != name:
            errors.append(f"{skill_file.relative_to(root)} name does not match its directory")
        if len(skill_text.splitlines()) >= 500:
            errors.append(f"{skill_file.relative_to(root)} must stay under 500 lines")
        if len(skill_text) > 20000:
            errors.append(f"{skill_file.relative_to(root)} is likely over the recommended 5,000-token budget")
        if PLACEHOLDER_RE.search(skill_text):
            errors.append(f"{skill_file.relative_to(root)} contains unresolved placeholders")

    if skill_dir.is_dir():
        for forbidden in FORBIDDEN_SKILL_DOCS:
            if (skill_dir / forbidden).exists():
                errors.append(f"runtime skill contains repository documentation: {skill_dir.name}/{forbidden}")
    return errors
