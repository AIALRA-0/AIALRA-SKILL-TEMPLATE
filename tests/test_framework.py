from __future__ import annotations

import copy
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_secrets import scan_file  # noqa: E402
from skill_framework import (  # noqa: E402
    load_spec,
    render_openai_yaml,
    render_skill,
    render_task_cases,
    render_trigger_queries,
    validate_skill_against_spec,
    validate_spec,
)


class FrameworkTests(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = load_spec(ROOT / "examples" / "research-skill.spec.json")

    def test_example_spec_is_structurally_valid(self) -> None:
        self.assertEqual([], validate_spec(self.spec))

    def test_rendered_skill_and_ui_metadata_are_specific(self) -> None:
        skill = render_skill(self.spec, ROOT)
        metadata = render_openai_yaml(self.spec)
        self.assertIn("## Evidence and source policy", skill)
        self.assertIn("Do not rank mismatched variants", skill)
        self.assertIn("$research-live-retail-prices", metadata)
        self.assertLess(len(skill.splitlines()), 500)

    def test_every_profile_renders_without_generic_placeholders(self) -> None:
        profile_cases = {
            "research": self.spec["profile_fields"],
            "tool-integration": {
                "capabilities": ["Read one explicitly selected service resource"],
                "auth_boundary": "Use user-authorized sessions; never collect credentials.",
                "read_actions": ["List and inspect explicitly scoped records"],
                "write_actions": ["Create or update only after explicit user authorization"],
                "confirmation_points": ["Before every external write or send"],
                "fallbacks": ["Use a direct official API", "Use a user-controlled browser session"],
                "failure_handling": "Report the unavailable capability and preserve partial read-only results.",
            },
            "artifact-production": {
                "input_inspection": ["Inspect every supplied source before editing"],
                "production_method": "Use the format-native library selected by the repository.",
                "render_or_run": ["Render or execute the final artifact", "Inspect the resulting output"],
                "handoff_standard": "Return the final artifact and name any unverified limitation.",
                "quality_checks": ["Content is complete", "Layout or runtime output is verified"],
            },
            "operational-workflow": {
                "preconditions": ["Confirm the exact target and current state"],
                "stage_gates": ["Validate the plan before execution", "Validate results before handoff"],
                "rollback": ["Use the documented recovery procedure if validation fails"],
                "completion_criteria": ["All required checks pass", "Residual risk is reported"],
            },
        }
        for profile, profile_fields in profile_cases.items():
            with self.subTest(profile=profile):
                candidate = copy.deepcopy(self.spec)
                candidate["profile"] = profile
                candidate["profile_fields"] = profile_fields
                self.assertEqual([], validate_spec(candidate))
                rendered = render_skill(candidate, ROOT)
                self.assertNotIn("{{", rendered)
                self.assertLess(len(rendered.splitlines()), 500)

    def test_candidate_requires_routing_eval_depth(self) -> None:
        invalid = copy.deepcopy(self.spec)
        invalid["maintenance"]["status"] = "candidate"
        invalid["triggers"]["positive"] = invalid["triggers"]["positive"][:3]
        errors = validate_spec(invalid)
        self.assertTrue(any("triggers.positive" in error for error in errors))

    def test_generated_drift_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            profile_dir = root / "templates" / "profiles"
            profile_dir.mkdir(parents=True)
            profile_dir.joinpath("research.md.tmpl").write_text(
                (ROOT / "templates" / "profiles" / "research.md.tmpl").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            name = self.spec["name"]
            skill_dir = root / ".agents" / "skills" / name
            (skill_dir / "agents").mkdir(parents=True)
            (skill_dir / "references").mkdir()
            (skill_dir / "SKILL.md").write_text(render_skill(self.spec, root), encoding="utf-8")
            (skill_dir / "agents" / "openai.yaml").write_text(
                render_openai_yaml(self.spec), encoding="utf-8"
            )
            (skill_dir / "references" / "evidence-schema.md").write_text(
                "# Evidence schema\n", encoding="utf-8"
            )
            eval_dir = root / "evals" / name
            eval_dir.mkdir(parents=True)
            (eval_dir / "trigger_queries.json").write_text(
                render_trigger_queries(self.spec), encoding="utf-8"
            )
            (eval_dir / "task_cases.json").write_text(
                render_task_cases(self.spec), encoding="utf-8"
            )
            self.assertEqual([], validate_skill_against_spec(root, self.spec))
            (skill_dir / "SKILL.md").write_text("drift\n", encoding="utf-8")
            errors = validate_skill_against_spec(root, self.spec)
            self.assertTrue(any("generated file drift" in error for error in errors))

    def test_secret_scanner_redacts_detection_and_accepts_placeholder(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            actual = root / "actual.txt"
            actual.write_text("token=" + "sk-" + ("A" * 30), encoding="utf-8")
            self.assertTrue(any(rule == "openai-key" for _, rule in scan_file(actual)))
            placeholder = root / "placeholder.txt"
            placeholder.write_text('api_key="${SERVICE_TOKEN}"\n', encoding="utf-8")
            self.assertEqual([], scan_file(placeholder))


if __name__ == "__main__":
    unittest.main()
