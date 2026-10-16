#!/usr/bin/env python3
"""Executable evaluations for deterministic parallel execution planning."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLANNER_PATH = ROOT / "tools" / "plan_parallel_execution.py"
SPEC = importlib.util.spec_from_file_location("plan_parallel_execution", PLANNER_PATH)
assert SPEC and SPEC.loader
PLANNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PLANNER)


class ParallelExecutionPlanScenarios(unittest.TestCase):
    def test_independent_tasks_fan_out_then_dependency_fans_in(self) -> None:
        result = PLANNER.plan_execution(
            {
                "schema_version": 1,
                "max_concurrency": 4,
                "tasks": [
                    {"id": "source-analysis", "write_paths": ["work/source"]},
                    {"id": "brand-analysis", "write_paths": ["work/brand"]},
                    {
                        "id": "merge",
                        "dependencies": ["source-analysis", "brand-analysis"],
                        "write_paths": ["canonical/state.json"],
                    },
                ],
            }
        )
        self.assertEqual(
            [stage["task_ids"] for stage in result["stages"]],
            [["brand-analysis", "source-analysis"], ["merge"]],
        )
        self.assertEqual(result["parallel_stage_count"], 1)

    def test_overlapping_write_paths_are_serialized(self) -> None:
        result = PLANNER.plan_execution(
            {
                "max_concurrency": 3,
                "tasks": [
                    {"id": "api", "write_paths": ["src/api"]},
                    {"id": "api-config", "write_paths": ["src/api/config.yaml"]},
                    {"id": "ui", "write_paths": ["src/ui"]},
                ],
            }
        )
        self.assertEqual(result["stages"][0]["task_ids"], ["api", "ui"])
        self.assertEqual(result["stages"][1]["task_ids"], ["api-config"])
        self.assertEqual(result["conflicts"][0]["conflicts"][0]["kind"], "write_path")
        deferred = result["stages"][0]["deferred"]
        self.assertEqual(deferred[0]["reason"], "ownership_conflict")

    def test_similar_sibling_path_names_do_not_conflict(self) -> None:
        result = PLANNER.plan_execution(
            {
                "max_concurrency": 2,
                "tasks": [
                    {"id": "api", "write_paths": ["src/api"]},
                    {"id": "api-v2", "write_paths": ["src/api-v2"]},
                ],
            }
        )
        self.assertEqual(result["stages"][0]["task_ids"], ["api", "api-v2"])
        self.assertEqual(result["conflicts"], [])

    def test_shared_mutable_surface_is_serialized(self) -> None:
        result = PLANNER.plan_execution(
            {
                "max_concurrency": 2,
                "tasks": [
                    {"id": "change-a", "shared_surfaces": ["openspec:main-spec:accounts"]},
                    {"id": "change-b", "shared_surfaces": ["openspec:main-spec:accounts"]},
                ],
            }
        )
        self.assertEqual([stage["task_ids"] for stage in result["stages"]], [["change-a"], ["change-b"]])
        self.assertEqual(
            result["conflicts"][0]["conflicts"],
            [{"kind": "shared_surface", "value": "openspec:main-spec:accounts"}],
        )

    def test_wave_prefers_a_larger_conflict_free_ready_set(self) -> None:
        result = PLANNER.plan_execution(
            {
                "max_concurrency": 2,
                "tasks": [
                    {"id": "broad", "write_paths": ["src"]},
                    {"id": "left", "write_paths": ["src/left"]},
                    {"id": "right", "write_paths": ["src/right"]},
                ],
            }
        )
        self.assertEqual([stage["task_ids"] for stage in result["stages"]], [["left", "right"], ["broad"]])

    def test_max_concurrency_bounds_a_conflict_free_wave(self) -> None:
        result = PLANNER.plan_execution(
            {
                "max_concurrency": 2,
                "tasks": [{"id": identifier} for identifier in ("a", "b", "c")],
            }
        )
        self.assertEqual([stage["task_ids"] for stage in result["stages"]], [["a", "b"], ["c"]])
        self.assertEqual(result["stages"][0]["deferred"], [{"task_id": "c", "reason": "max_concurrency"}])

    def test_cycle_is_reported_with_a_stable_path(self) -> None:
        with self.assertRaisesRegex(PLANNER.PlanError, r"dependency cycle detected: a -> b -> a"):
            PLANNER.plan_execution(
                {
                    "tasks": [
                        {"id": "b", "dependencies": ["a"]},
                        {"id": "a", "dependencies": ["b"]},
                    ]
                }
            )

    def test_input_order_does_not_change_the_plan(self) -> None:
        tasks = [
            {"id": "b", "write_paths": ["src/b"]},
            {"id": "a", "write_paths": ["src/a"]},
            {"id": "c", "dependencies": ["a", "b"]},
        ]
        forward = PLANNER.plan_execution({"max_concurrency": 2, "tasks": tasks})
        reverse = PLANNER.plan_execution({"max_concurrency": 2, "tasks": list(reversed(tasks))})
        self.assertEqual(forward, reverse)

    def test_cli_emits_json_and_honors_concurrency_override(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            plan_path = Path(temporary) / "plan.json"
            plan_path.write_text(
                json.dumps({"max_concurrency": 4, "tasks": [{"id": "a"}, {"id": "b"}]}),
                encoding="utf-8",
            )
            result = subprocess.run(
                ["python3", str(PLANNER_PATH), str(plan_path), "--max-concurrency", "1"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["max_concurrency"], 1)
        self.assertEqual([stage["task_ids"] for stage in payload["stages"]], [["a"], ["b"]])

    def test_unknown_dependency_and_unsafe_path_fail_closed(self) -> None:
        with self.assertRaisesRegex(PLANNER.PlanError, "unknown dependency"):
            PLANNER.plan_execution({"tasks": [{"id": "a", "dependencies": ["missing"]}]})
        with self.assertRaisesRegex(PLANNER.PlanError, "exact relative path"):
            PLANNER.plan_execution({"tasks": [{"id": "a", "write_paths": ["src/*"]}]})


if __name__ == "__main__":
    unittest.main()
