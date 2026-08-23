from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = [path for path in (ROOT / ".agents" / "skills").iterdir() if path.is_dir()]
if len(SKILLS) != 1:
    raise RuntimeError(f"Expected one Skill, found {len(SKILLS)}")
SKILL_DIR = SKILLS[0]
sys.path.insert(0, str(SKILL_DIR / "scripts"))

from runtime_lib import (  # noqa: E402
    atomic_write_json,
    compute_core_manifest,
    load_workflow,
    sanitize_lesson,
    validate_schema,
    validate_workflow,
    verify_core_lock,
)


class RuntimeContractTests(unittest.TestCase):
    def test_workflow_is_structurally_valid(self) -> None:
        workflow = load_workflow(SKILL_DIR)
        self.assertEqual([], validate_workflow(workflow, SKILL_DIR, allow_draft=True))

    def test_core_lock_matches(self) -> None:
        self.assertEqual([], verify_core_lock(ROOT, SKILL_DIR))

    def test_core_manifest_uses_portable_paths(self) -> None:
        manifest = compute_core_manifest(ROOT, SKILL_DIR)
        self.assertTrue(all("\\" not in path for path in manifest["files"]))

    def test_atomic_json_writer_uses_portable_newlines(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "state.json"
            atomic_write_json(output, {"value": 1})
            self.assertNotIn(b"\r\n", output.read_bytes())

    def test_schema_validator_rejects_unknown_properties(self) -> None:
        schema = {
            "type": "object",
            "additionalProperties": False,
            "required": ["value"],
            "properties": {"value": {"type": "integer", "minimum": 1}},
        }
        self.assertEqual([], validate_schema({"value": 2}, schema))
        self.assertTrue(validate_schema({"value": 0, "extra": True}, schema))

    def test_learning_sanitizer_removes_private_values(self) -> None:
        raw = "When user person@example.com opens https://shop.invalid/order?id=123456789, do not retain it."
        cleaned = sanitize_lesson(raw)
        self.assertNotIn("person@example.com", cleaned)
        self.assertNotIn("https://", cleaned)
        self.assertNotIn("123456789", cleaned)


if __name__ == "__main__":
    unittest.main()
