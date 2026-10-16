#!/usr/bin/env python3

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DELIVERY = ROOT / "skills" / "manage-project-delivery" / "scripts" / "analyze_project_delivery.py"
FINANCIAL = ROOT / "skills" / "forecast-project-financials" / "scripts" / "calculate_project_forecast.py"
FIXTURES = ROOT / "evals" / "fixtures" / "project-controls"


class ProjectControlsTest(unittest.TestCase):
    def run_json(self, script: Path, fixture: str) -> dict[str, object]:
        result = subprocess.run(
            [sys.executable, str(script), str(FIXTURES / fixture)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout)

    def run_payload(self, script: Path, payload: dict[str, object]) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temporary:
            input_path = Path(temporary) / "input.json"
            input_path.write_text(json.dumps(payload), encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(script), str(input_path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

    def test_delivery_analysis_derives_health_risk_and_critical_path(self) -> None:
        result = self.run_json(DELIVERY, "delivery-valid.json")
        self.assertEqual("AT_RISK", result["health"])
        self.assertEqual(["WS-2"], result["overdue_workstreams"])
        self.assertEqual(["RISK-1"], result["high_risks"])
        self.assertEqual(["WS-1", "WS-2", "WS-3"], result["critical_path"]["workstream_ids"])
        self.assertEqual(9, result["critical_path"]["duration_days"])
        self.assertEqual({"DONE": 1, "IN_PROGRESS": 1, "PLANNED": 1}, result["status_counts"])

    def test_delivery_analysis_rejects_dependency_cycles(self) -> None:
        result = subprocess.run(
            [sys.executable, str(DELIVERY), str(FIXTURES / "delivery-cycle.json")],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(2, result.returncode)
        self.assertIn("dependency cycle", result.stderr)

    def test_delivery_analysis_rejects_unknown_dependencies(self) -> None:
        payload = json.loads((FIXTURES / "delivery-valid.json").read_text())
        payload["workstreams"][0]["dependencies"] = ["WS-MISSING"]
        result = self.run_payload(DELIVERY, payload)
        self.assertEqual(2, result.returncode)
        self.assertIn("unknown dependency WS-MISSING", result.stderr)

    def test_delivery_analysis_rejects_empty_workstreams_and_zero_duration(self) -> None:
        empty = self.run_payload(DELIVERY, {"schema_version": 1, "as_of": "2026-09-02", "workstreams": []})
        self.assertEqual(2, empty.returncode)
        self.assertIn("workstreams must be a non-empty array", empty.stderr)
        payload = json.loads((FIXTURES / "delivery-valid.json").read_text())
        payload["workstreams"][0]["duration_days"] = 0
        invalid = self.run_payload(DELIVERY, payload)
        self.assertEqual(2, invalid.returncode)
        self.assertIn("duration_days must be greater than zero", invalid.stderr)

    def test_delivery_analysis_prioritizes_blocked_health_and_unowned_work(self) -> None:
        payload = json.loads((FIXTURES / "delivery-valid.json").read_text())
        payload["workstreams"][1]["status"] = "BLOCKED"
        payload["workstreams"][1]["blocked_reason"] = "Synthetic dependency decision"
        payload["workstreams"][1]["owner"] = ""
        result = self.run_payload(DELIVERY, payload)
        self.assertEqual(0, result.returncode, result.stderr)
        summary = json.loads(result.stdout)
        self.assertEqual("BLOCKED", summary["health"])
        self.assertEqual(["WS-2"], summary["blocked_workstreams"])
        self.assertEqual(["WS-2"], summary["unowned_workstreams"])

    def test_delivery_analysis_accepts_boundary_risks_and_same_day_work(self) -> None:
        payload = json.loads((FIXTURES / "delivery-valid.json").read_text())
        payload["workstreams"][2]["planned_start"] = "2026-09-01"
        payload["workstreams"][2]["planned_end"] = "2026-09-01"
        payload["risks"] = [
            {"id": "R-LOW", "status": "CLOSED", "owner": "", "likelihood": 1, "impact": 1},
            {"id": "R-HIGH", "status": "OPEN", "owner": "", "likelihood": 5, "impact": 5},
        ]
        result = self.run_payload(DELIVERY, payload)
        self.assertEqual(0, result.returncode, result.stderr)
        summary = json.loads(result.stdout)
        self.assertEqual(["R-HIGH"], summary["high_risks"])
        self.assertIn("R-HIGH: open risk has no owner", summary["warnings"])
        self.assertNotIn("R-LOW: open risk has no owner", summary["warnings"])

    def test_delivery_work_due_on_as_of_date_is_not_overdue(self) -> None:
        payload = json.loads((FIXTURES / "delivery-valid.json").read_text())
        payload["workstreams"][1]["planned_end"] = payload["as_of"]
        payload["risks"] = []
        result = self.run_payload(DELIVERY, payload)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertNotIn("WS-2", json.loads(result.stdout)["overdue_workstreams"])

    def test_delivery_analysis_marks_completed_active_work_complete(self) -> None:
        payload = json.loads((FIXTURES / "delivery-valid.json").read_text())
        for workstream in payload["workstreams"]:
            workstream["status"] = "DONE"
            workstream["progress"] = 1
            workstream["evidence"] = ["synthetic acceptance"]
        payload["risks"] = []
        result = self.run_payload(DELIVERY, payload)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("COMPLETE", json.loads(result.stdout)["health"])

    def test_financial_forecast_reconciles_actual_forecast_and_evm(self) -> None:
        result = self.run_json(FINANCIAL, "financial-valid.json")
        self.assertEqual("EUR", result["currency"])
        self.assertEqual(300.0, result["baseline"]["cost"])
        self.assertEqual(330.0, result["forecast_at_completion"]["cost"])
        self.assertEqual(465.0, result["forecast_at_completion"]["revenue"])
        self.assertEqual(-30.0, result["variance_at_completion"]["cost_favorable"])
        self.assertEqual(-35.0, result["variance_at_completion"]["revenue"])
        self.assertEqual(0.7, result["earned_value"]["cost_performance_index"])
        self.assertEqual(0.875, result["earned_value"]["schedule_performance_index"])
        self.assertEqual(-45.0, result["earned_value"]["cost_variance"])
        self.assertEqual(-15.0, result["earned_value"]["schedule_variance"])
        self.assertEqual(-30.0, result["earned_value"]["variance_at_completion"])
        self.assertEqual(1.3, result["earned_value"]["to_complete_performance_index"])
        self.assertEqual(170.5, result["scenarios"][0]["margin"])
        self.assertEqual("upside", result["scenarios"][0]["id"])

    def test_financial_forecast_rejects_duplicate_periods(self) -> None:
        result = subprocess.run(
            [sys.executable, str(FINANCIAL), str(FIXTURES / "financial-invalid.json")],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(2, result.returncode)
        self.assertIn("duplicate period", result.stderr)

    def test_financial_forecast_rejects_empty_periods(self) -> None:
        payload = {"schema_version": 1, "currency": "EUR", "as_of_period": "2026-02", "periods": []}
        result = self.run_payload(FINANCIAL, payload)
        self.assertEqual(2, result.returncode)
        self.assertIn("periods must be a non-empty array", result.stderr)

    def test_financial_forecast_rejects_missing_historical_actuals(self) -> None:
        payload = json.loads((FIXTURES / "financial-valid.json").read_text())
        del payload["periods"][0]["actual_cost"]
        result = self.run_payload(FINANCIAL, payload)
        self.assertEqual(2, result.returncode)
        self.assertIn("actual_cost must be a non-negative finite number", result.stderr)

    def test_financial_forecast_marks_zero_denominator_metrics_unavailable(self) -> None:
        payload = json.loads((FIXTURES / "financial-valid.json").read_text())
        for period in payload["periods"]:
            period["baseline_revenue"] = 0
            period["baseline_cost"] = 0
            if period["period"] <= payload["as_of_period"]:
                period["actual_revenue"] = 0
                period["actual_cost"] = 0
                period["planned_value"] = 0
                period["earned_value"] = 0
            else:
                period["forecast_revenue"] = 0
                period["forecast_cost"] = 0
        result = self.run_payload(FINANCIAL, payload)
        self.assertEqual(0, result.returncode, result.stderr)
        summary = json.loads(result.stdout)
        self.assertIsNone(summary["forecast_at_completion"]["margin_rate"])
        self.assertIsNone(summary["earned_value"]["cost_performance_index"])
        self.assertIsNone(summary["earned_value"]["schedule_performance_index"])
        self.assertIsNone(summary["earned_value"]["to_complete_performance_index"])
        self.assertGreaterEqual(len(summary["warnings"]), 4)

    def test_tools_support_explicit_output_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "forecast.json"
            subprocess.run(
                [sys.executable, str(FINANCIAL), str(FIXTURES / "financial-valid.json"), "--output", str(output)],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual("EUR", json.loads(output.read_text())["currency"])


if __name__ == "__main__":
    unittest.main()
