#!/usr/bin/env python3
"""Validate and summarize a period-based project financial forecast."""

from __future__ import annotations

import argparse
import json
import re
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


PERIOD_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


def load_input(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("input root must be an object")
    return value


def decimal_value(value: Any, field: str, errors: list[str], *, required: bool = True) -> Decimal | None:
    if value is None and not required:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        errors.append(f"{field} must be a non-negative finite number")
        return None
    try:
        parsed = Decimal(str(value))
    except InvalidOperation:
        errors.append(f"{field} must be a non-negative finite number")
        return None
    if not parsed.is_finite() or parsed < 0:
        errors.append(f"{field} must be a non-negative finite number")
        return None
    return parsed


def rendered(value: Decimal | None, places: int = 4) -> float | None:
    if value is None:
        return None
    quantum = Decimal(1).scaleb(-places)
    return float(value.quantize(quantum))


def ratio(numerator: Decimal, denominator: Decimal, label: str, warnings: list[str]) -> Decimal | None:
    if denominator == 0:
        warnings.append(f"{label} unavailable because denominator is zero")
        return None
    return numerator / denominator


def calculate(payload: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if payload.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    currency = payload.get("currency")
    if not isinstance(currency, str) or not currency.strip():
        errors.append("currency is required")
    as_of = payload.get("as_of_period")
    if not isinstance(as_of, str) or not PERIOD_RE.fullmatch(as_of):
        errors.append("as_of_period must use YYYY-MM")

    period_values = payload.get("periods")
    if not isinstance(period_values, list) or not period_values:
        return {}, errors + ["periods must be a non-empty array"]

    periods: list[dict[str, Any]] = []
    seen_periods: set[str] = set()
    for index, item in enumerate(period_values):
        field = f"periods[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{field} must be an object")
            continue
        period = item.get("period")
        if not isinstance(period, str) or not PERIOD_RE.fullmatch(period):
            errors.append(f"{field}.period must use YYYY-MM")
            continue
        if period in seen_periods:
            errors.append(f"duplicate period: {period}")
            continue
        seen_periods.add(period)
        historical = isinstance(as_of, str) and period <= as_of
        baseline_revenue = decimal_value(item.get("baseline_revenue"), f"{period}.baseline_revenue", errors)
        baseline_cost = decimal_value(item.get("baseline_cost"), f"{period}.baseline_cost", errors)
        actual_revenue = decimal_value(item.get("actual_revenue"), f"{period}.actual_revenue", errors, required=historical)
        actual_cost = decimal_value(item.get("actual_cost"), f"{period}.actual_cost", errors, required=historical)
        forecast_revenue = decimal_value(item.get("forecast_revenue"), f"{period}.forecast_revenue", errors, required=not historical)
        forecast_cost = decimal_value(item.get("forecast_cost"), f"{period}.forecast_cost", errors, required=not historical)
        planned_value = decimal_value(item.get("planned_value"), f"{period}.planned_value", errors, required=historical)
        earned_value = decimal_value(item.get("earned_value"), f"{period}.earned_value", errors, required=historical)
        periods.append({
            "period": period,
            "historical": historical,
            "baseline_revenue": baseline_revenue or Decimal(0),
            "baseline_cost": baseline_cost or Decimal(0),
            "actual_revenue": actual_revenue or Decimal(0),
            "actual_cost": actual_cost or Decimal(0),
            "forecast_revenue": forecast_revenue or Decimal(0),
            "forecast_cost": forecast_cost or Decimal(0),
            "planned_value": planned_value or Decimal(0),
            "earned_value": earned_value or Decimal(0),
        })

    if isinstance(as_of, str) and as_of not in seen_periods:
        errors.append("as_of_period must identify one supplied period")
    if errors:
        return {}, sorted(set(errors))
    periods.sort(key=lambda item: item["period"])

    baseline_revenue = sum((item["baseline_revenue"] for item in periods), Decimal(0))
    baseline_cost = sum((item["baseline_cost"] for item in periods), Decimal(0))
    historical = [item for item in periods if item["historical"]]
    future = [item for item in periods if not item["historical"]]
    actual_revenue = sum((item["actual_revenue"] for item in historical), Decimal(0))
    actual_cost = sum((item["actual_cost"] for item in historical), Decimal(0))
    future_revenue = sum((item["forecast_revenue"] for item in future), Decimal(0))
    future_cost = sum((item["forecast_cost"] for item in future), Decimal(0))
    eac_revenue = actual_revenue + future_revenue
    eac_cost = actual_cost + future_cost
    eac_margin = eac_revenue - eac_cost
    planned_value = sum((item["planned_value"] for item in historical), Decimal(0))
    earned_value = sum((item["earned_value"] for item in historical), Decimal(0))
    cost_variance = earned_value - actual_cost
    schedule_variance = earned_value - planned_value
    cpi = ratio(earned_value, actual_cost, "cost performance index", warnings)
    spi = ratio(earned_value, planned_value, "schedule performance index", warnings)
    remaining_budget = baseline_cost - earned_value
    remaining_budget_capacity = baseline_cost - actual_cost
    tcpi = ratio(remaining_budget, remaining_budget_capacity, "to-complete performance index", warnings)
    margin_rate = ratio(eac_margin, eac_revenue, "forecast margin rate", warnings)

    scenarios: list[dict[str, Any]] = []
    seen_scenarios: set[str] = set()
    scenario_values = payload.get("scenarios", [])
    if not isinstance(scenario_values, list):
        return {}, ["scenarios must be an array"]
    for index, item in enumerate(scenario_values):
        if not isinstance(item, dict):
            errors.append(f"scenarios[{index}] must be an object")
            continue
        identifier = item.get("id")
        if not isinstance(identifier, str) or not identifier:
            errors.append(f"scenarios[{index}].id is required")
            continue
        if identifier in seen_scenarios:
            errors.append(f"duplicate scenario ID: {identifier}")
            continue
        seen_scenarios.add(identifier)
        revenue_multiplier = decimal_value(item.get("future_revenue_multiplier"), f"{identifier}.future_revenue_multiplier", errors)
        cost_multiplier = decimal_value(item.get("future_cost_multiplier"), f"{identifier}.future_cost_multiplier", errors)
        if revenue_multiplier is None or cost_multiplier is None:
            continue
        scenario_revenue = actual_revenue + future_revenue * revenue_multiplier
        scenario_cost = actual_cost + future_cost * cost_multiplier
        scenario_margin = scenario_revenue - scenario_cost
        scenarios.append({
            "id": identifier,
            "revenue": rendered(scenario_revenue),
            "cost": rendered(scenario_cost),
            "margin": rendered(scenario_margin),
            "margin_rate": rendered(ratio(scenario_margin, scenario_revenue, f"{identifier} margin rate", warnings)),
        })
    if errors:
        return {}, sorted(set(errors))

    summary = {
        "schema_version": 1,
        "currency": currency.strip(),
        "as_of_period": as_of,
        "baseline": {"revenue": rendered(baseline_revenue), "cost": rendered(baseline_cost)},
        "actual_to_date": {"revenue": rendered(actual_revenue), "cost": rendered(actual_cost)},
        "remaining_forecast": {"revenue": rendered(future_revenue), "cost": rendered(future_cost)},
        "forecast_at_completion": {
            "revenue": rendered(eac_revenue),
            "cost": rendered(eac_cost),
            "margin": rendered(eac_margin),
            "margin_rate": rendered(margin_rate),
        },
        "variance_at_completion": {
            "revenue": rendered(eac_revenue - baseline_revenue),
            "cost_favorable": rendered(baseline_cost - eac_cost),
        },
        "earned_value": {
            "planned_value": rendered(planned_value),
            "earned_value": rendered(earned_value),
            "actual_cost": rendered(actual_cost),
            "cost_variance": rendered(cost_variance),
            "schedule_variance": rendered(schedule_variance),
            "cost_performance_index": rendered(cpi),
            "schedule_performance_index": rendered(spi),
            "estimate_to_complete": rendered(future_cost),
            "estimate_at_completion": rendered(eac_cost),
            "variance_at_completion": rendered(baseline_cost - eac_cost),
            "to_complete_performance_index": rendered(tcpi),
        },
        "scenarios": scenarios,
        "warnings": sorted(set(warnings)),
    }
    return summary, []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("forecast", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        summary, errors = calculate(load_input(args.forecast))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"ERROR {error}", file=sys.stderr)
        return 2
    rendered_output = json.dumps(summary, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered_output, encoding="utf-8")
    else:
        sys.stdout.write(rendered_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
