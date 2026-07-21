from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from create_skill_repo import build  # noqa: E402


def run_json(command: list[str], cwd: Path, expected_code: int = 0) -> dict:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    if result.returncode != expected_code:
        raise AssertionError(
            f"Command returned {result.returncode}, expected {expected_code}: {' '.join(command)}\n"
            f"stdout={result.stdout}\nstderr={result.stderr}"
        )
    stream = result.stdout if result.stdout.strip() else result.stderr
    return json.loads(stream)


class TemplateRuntimeTests(unittest.TestCase):
    def create_repository(self, parent: Path) -> Path:
        output = parent / "normalize-text-skill"
        args = argparse.Namespace(
            name="normalize-text-skill",
            output=output,
            description=(
                "Normalize whitespace in supplied text through a deterministic graph. Use when testing "
                "the generated Skill runtime. Do not use for semantic rewriting or production content."
            ),
            display_name="Normalize Text Skill",
            short_description="Normalize text with a deterministic graph",
            default_prompt="Use $normalize-text-skill to normalize this test text.",
            portable=True,
        )
        build(args)
        return output

    def configure_deterministic_workflow(self, repo: Path) -> Path:
        skill = repo / ".agents" / "skills" / "normalize-text-skill"
        executor = skill / "executors" / "normalize.py"
        executor.parent.mkdir()
        executor.write_text(
            """#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--input', required=True, type=Path)
parser.add_argument('--output', required=True, type=Path)
args = parser.parse_args()
data = json.loads(args.input.read_text(encoding='utf-8'))
result = {'normalized': ' '.join(data['text'].split())}
args.output.write_text(json.dumps(result, ensure_ascii=False) + '\\n', encoding='utf-8')
""",
            encoding="utf-8",
        )
        (skill / "schemas" / "input.schema.json").write_text(
            json.dumps(
                {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["text"],
                    "properties": {"text": {"type": "string", "minLength": 1, "maxLength": 1000}},
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (skill / "schemas" / "output.schema.json").write_text(
            json.dumps(
                {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["normalized"],
                    "properties": {"normalized": {"type": "string", "minLength": 1}},
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        workflow = {
            "ir_version": 1,
            "skill_name": "normalize-text-skill",
            "configured": True,
            "entry_node": "normalize-text",
            "limits": {"max_nodes": 4, "total_timeout_seconds": 60},
            "learning": {"compact_every": 32, "active_rule_limit": 16},
            "nodes": [
                {
                    "id": "normalize-text",
                    "input_schema": "schemas/input.schema.json",
                    "output_schema": "schemas/output.schema.json",
                    "executor": "script",
                    "command": [
                        "python3",
                        "executors/normalize.py",
                        "--input",
                        "${input_file}",
                        "--output",
                        "${output_file}",
                    ],
                    "side_effect": "none",
                    "requires_confirmation": False,
                    "timeout_seconds": 10,
                    "max_retries": 1,
                    "validator": None,
                    "fallback": None,
                    "on_success": "__complete__",
                    "stop_conditions": [],
                }
            ],
            "final_output_schema": "schemas/output.schema.json",
            "final_validator": None,
        }
        (skill / "workflow.yaml").write_text(json.dumps(workflow, indent=2) + "\n", encoding="utf-8")
        run_json([sys.executable, str(skill / "scripts" / "freeze_core.py")], repo)
        return skill

    def test_draft_repository_is_initialized_and_locked(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self.create_repository(Path(temporary))
            self.assertTrue((repo / ".git").is_dir())
            self.assertTrue((repo / ".core-lock.json").is_file())
            payload = run_json([sys.executable, "scripts/validate.py", "--allow-draft"], repo)
            self.assertTrue(payload["valid"])
            input_file = repo / "input.json"
            input_file.write_text('{"request":"test"}\n', encoding="utf-8")
            error = run_json(
                [
                    sys.executable,
                    ".agents/skills/normalize-text-skill/scripts/runner.py",
                    "start",
                    "--input",
                    str(input_file),
                ],
                repo,
                expected_code=2,
            )
            self.assertEqual("error", error["status"])

    def test_sensitive_scanner_does_not_trust_example_variable_names(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self.create_repository(Path(temporary))
            candidate = repo / "example_credentials.txt"
            candidate.write_text(
                'example_api_key = "' + ("sensitive-value-" * 2) + '"\n', encoding="utf-8"
            )
            result = subprocess.run(
                [sys.executable, "scripts/check_secrets.py", str(candidate)],
                cwd=repo,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(1, result.returncode)
            self.assertNotIn("sensitive-value", result.stderr)
            self.assertIn("value redacted", result.stderr)

    def test_runner_executes_deterministic_graph(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self.create_repository(Path(temporary))
            skill = self.configure_deterministic_workflow(repo)
            input_file = repo / "input.json"
            input_file.write_text('{"text":"  alpha   beta  "}\n', encoding="utf-8")
            started = run_json(
                [sys.executable, str(skill / "scripts" / "runner.py"), "start", "--input", str(input_file)],
                repo,
            )
            rejected_skip = run_json(
                [
                    sys.executable,
                    str(skill / "scripts" / "runner.py"),
                    "fail",
                    "--state-id",
                    started["state_id"],
                    "--node-id",
                    "normalize-text",
                    "--kind",
                    "fallback",
                    "--message",
                    "attempted manual skip",
                ],
                repo,
                expected_code=2,
            )
            self.assertEqual("error", rejected_skip["status"])
            completed = run_json(
                [
                    sys.executable,
                    str(skill / "scripts" / "runner.py"),
                    "advance",
                    "--state-id",
                    started["state_id"],
                ],
                repo,
            )
            self.assertEqual("completed", completed["status"])
            self.assertEqual("alpha beta", completed["final_output"]["normalized"])

    def test_runner_bounds_retries_then_uses_declared_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self.create_repository(Path(temporary))
            skill = self.configure_deterministic_workflow(repo)
            failing = skill / "executors" / "fail.py"
            failing.write_text(
                "import sys\nprint('controlled failure', file=sys.stderr)\nraise SystemExit(7)\n",
                encoding="utf-8",
            )
            workflow_path = skill / "workflow.yaml"
            workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
            recovery = dict(workflow["nodes"][0])
            recovery["id"] = "recover-text"
            unstable = dict(workflow["nodes"][0])
            unstable.update(
                {
                    "id": "unstable-step",
                    "command": ["python3", "executors/fail.py"],
                    "max_retries": 1,
                    "fallback": "recover-text",
                    "on_success": "__complete__",
                }
            )
            workflow["entry_node"] = "unstable-step"
            workflow["nodes"] = [unstable, recovery]
            workflow_path.write_text(json.dumps(workflow, indent=2) + "\n", encoding="utf-8")
            run_json([sys.executable, str(skill / "scripts" / "freeze_core.py")], repo)
            input_file = repo / "fallback-input.json"
            input_file.write_text('{"text":" alpha   beta "}\n', encoding="utf-8")
            started = run_json(
                [sys.executable, str(skill / "scripts" / "runner.py"), "start", "--input", str(input_file)],
                repo,
            )
            completed = run_json(
                [
                    sys.executable,
                    str(skill / "scripts" / "runner.py"),
                    "advance",
                    "--state-id",
                    started["state_id"],
                ],
                repo,
            )
            self.assertEqual("completed", completed["status"])
            self.assertEqual("alpha beta", completed["final_output"]["normalized"])
            state = run_json(
                [
                    sys.executable,
                    str(skill / "scripts" / "runner.py"),
                    "status",
                    "--state-id",
                    started["state_id"],
                ],
                repo,
            )
            self.assertEqual(1, state["retries"]["unstable-step"])
            failures = [event for event in state["trace"] if event["event"] == "node-failed"]
            self.assertEqual(2, len(failures))

    def test_core_mutation_is_a_hard_runtime_stop(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self.create_repository(Path(temporary))
            skill = self.configure_deterministic_workflow(repo)
            workflow_path = skill / "workflow.yaml"
            workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
            workflow["limits"]["max_nodes"] = 5
            workflow_path.write_text(json.dumps(workflow, indent=2) + "\n", encoding="utf-8")
            input_file = repo / "input.json"
            input_file.write_text('{"text":"alpha"}\n', encoding="utf-8")
            payload = run_json(
                [sys.executable, str(skill / "scripts" / "runner.py"), "start", "--input", str(input_file)],
                repo,
                expected_code=2,
            )
            self.assertEqual("error", payload["status"])
            self.assertIn("core", payload["error"].lower())

    def test_write_executor_requires_user_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self.create_repository(Path(temporary))
            skill = repo / ".agents" / "skills" / "normalize-text-skill"
            workflow = {
                "ir_version": 1,
                "skill_name": "normalize-text-skill",
                "configured": True,
                "entry_node": "external-write",
                "limits": {"max_nodes": 4, "total_timeout_seconds": 60},
                "learning": {"compact_every": 32, "active_rule_limit": 16},
                "nodes": [
                    {
                        "id": "external-write",
                        "input_schema": "schemas/input.schema.json",
                        "output_schema": "schemas/output.schema.json",
                        "executor": "mcp",
                        "action": {"name": "example.write", "arguments": {"from": "node-input"}},
                        "side_effect": "write",
                        "requires_confirmation": True,
                        "timeout_seconds": 10,
                        "max_retries": 0,
                        "validator": None,
                        "fallback": None,
                        "on_success": "__complete__",
                        "stop_conditions": ["Stop if the user does not confirm the external write."],
                    }
                ],
                "final_output_schema": "schemas/output.schema.json",
                "final_validator": None,
            }
            (skill / "workflow.yaml").write_text(json.dumps(workflow, indent=2) + "\n", encoding="utf-8")
            run_json([sys.executable, str(skill / "scripts" / "freeze_core.py")], repo)
            input_file = repo / "input.json"
            input_file.write_text('{"request":"write test"}\n', encoding="utf-8")
            started = run_json(
                [sys.executable, str(skill / "scripts" / "runner.py"), "start", "--input", str(input_file)],
                repo,
            )
            paused = run_json(
                [sys.executable, str(skill / "scripts" / "runner.py"), "advance", "--state-id", started["state_id"]],
                repo,
            )
            self.assertEqual("waiting-confirmation", paused["status"])
            approved = run_json(
                [
                    sys.executable,
                    str(skill / "scripts" / "runner.py"),
                    "approve",
                    "--state-id",
                    started["state_id"],
                    "--node-id",
                    "external-write",
                ],
                repo,
            )
            self.assertEqual("running", approved["status"])
            waiting = run_json(
                [sys.executable, str(skill / "scripts" / "runner.py"), "advance", "--state-id", started["state_id"]],
                repo,
            )
            self.assertEqual("waiting-external", waiting["status"])

    def test_workflow_rejects_completion_as_a_failure_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self.create_repository(Path(temporary))
            skill = self.configure_deterministic_workflow(repo)
            workflow_path = skill / "workflow.yaml"
            workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
            workflow["nodes"][0]["fallback"] = "__complete__"
            workflow_path.write_text(json.dumps(workflow, indent=2) + "\n", encoding="utf-8")
            payload = run_json(
                [sys.executable, str(skill / "scripts" / "validate_repo.py"), "--ignore-core-lock"],
                repo,
                expected_code=1,
            )
            self.assertTrue(
                any("cannot complete" in error for error in payload["errors"]), payload["errors"]
            )

    def test_learning_compacts_losslessly_and_never_changes_core(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self.create_repository(Path(temporary))
            skill = self.configure_deterministic_workflow(repo)
            learn = skill / "scripts" / "learn.py"
            runner = skill / "scripts" / "runner.py"
            lesson = "When repeated spaces occur, normalize them deterministically before returning output."
            recorded_state_ids = []
            for index in range(32):
                input_file = repo / f"learning-input-{index}.json"
                input_file.write_text('{"text":"alpha   beta"}\n', encoding="utf-8")
                started = run_json(
                    [sys.executable, str(runner), "start", "--input", str(input_file)], repo
                )
                completed = run_json(
                    [
                        sys.executable,
                        str(runner),
                        "advance",
                        "--state-id",
                        started["state_id"],
                    ],
                    repo,
                )
                self.assertEqual("completed", completed["status"])
                recorded_state_ids.append(started["state_id"])
                run_json(
                    [
                        sys.executable,
                        str(learn),
                        "record",
                        "--polarity",
                        "positive",
                        "--scope",
                        "whitespace-normalization",
                        "--lesson",
                        lesson,
                        "--evidence",
                        f"review:case-{index}",
                        "--state-id",
                        started["state_id"],
                    ],
                    repo,
                )
            ledger = (repo / "learning" / "ledger.jsonl").read_text(encoding="utf-8").strip()
            archives = list((repo / "learning" / "archive").glob("*.jsonl"))
            active = json.loads((repo / "learning" / "active-rules.json").read_text(encoding="utf-8"))
            self.assertEqual("", ledger)
            self.assertEqual(1, len(archives))
            self.assertEqual(32, len(archives[0].read_text(encoding="utf-8").splitlines()))
            self.assertLessEqual(len(active["rules"]), 16)
            self.assertEqual(32, active["rules"][0]["support_count"])
            duplicate = run_json(
                [
                    sys.executable,
                    str(learn),
                    "record",
                    "--polarity",
                    "positive",
                    "--scope",
                    "whitespace-normalization",
                    "--lesson",
                    lesson,
                    "--evidence",
                    "review:case-0",
                    "--state-id",
                    recorded_state_ids[0],
                ],
                repo,
            )
            self.assertFalse(duplicate["recorded"])
            second_lesson = run_json(
                [
                    sys.executable,
                    str(learn),
                    "record",
                    "--polarity",
                    "negative",
                    "--scope",
                    "whitespace-normalization",
                    "--lesson",
                    "Do not record a second advisory lesson for the same completed workflow state.",
                    "--evidence",
                    "review:second-lesson",
                    "--state-id",
                    recorded_state_ids[0],
                ],
                repo,
                expected_code=2,
            )
            self.assertEqual("error", second_lesson["status"])
            self.assertIn("one learning event", second_lesson["error"])
            active_after_duplicate = json.loads(
                (repo / "learning" / "active-rules.json").read_text(encoding="utf-8")
            )
            self.assertEqual(32, active_after_duplicate["rules"][0]["support_count"])
            proposal = run_json(
                [
                    sys.executable,
                    str(skill / "scripts" / "promote.py"),
                    "propose",
                    "--rule-id",
                    active["rules"][0]["rule_id"],
                ],
                repo,
            )
            self.assertEqual("proposed", proposal["proposal"]["status"])
            lock = run_json(
                [sys.executable, str(skill / "scripts" / "freeze_core.py"), "--check"], repo
            )
            self.assertTrue(lock["valid"])

    def test_workflow_rejects_hidden_cycles_and_unreachable_nodes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = self.create_repository(Path(temporary))
            skill = self.configure_deterministic_workflow(repo)
            workflow_path = skill / "workflow.yaml"
            workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
            original = workflow["nodes"][0]
            workflow["nodes"].extend(
                [
                    {
                        **original,
                        "id": "hidden-a",
                        "on_success": "hidden-b",
                    },
                    {
                        **original,
                        "id": "hidden-b",
                        "on_success": "hidden-a",
                    },
                ]
            )
            workflow_path.write_text(json.dumps(workflow, indent=2) + "\n", encoding="utf-8")
            payload = run_json(
                [sys.executable, str(skill / "scripts" / "validate_repo.py"), "--allow-draft"],
                repo,
                expected_code=1,
            )
            joined = " ".join(payload["errors"])
            self.assertIn("unreachable", joined)
            self.assertIn("cycle", joined)


if __name__ == "__main__":
    unittest.main()
