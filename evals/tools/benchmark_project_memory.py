#!/usr/bin/env python3
"""Benchmark project-memory continuation on a synthetic mixed-language legacy estate."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import tempfile
import time
from unittest.mock import patch
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


memory = load_module(
    "manage_project_memory_benchmark",
    ROOT / "skills/maintain-project-memory/scripts/manage_project_memory.py",
)
coordinator = load_module(
    "coordinate_analysis_benchmark",
    ROOT / "skills/analyze-legacy-system/scripts/coordinate_analysis.py",
)


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def artifact(identifier: str, path: str, language: str, sha256: str, kind: str = "source") -> dict:
    return {
        "id": identifier, "path": path, "size": 1, "sha256": sha256,
        "kind": kind, "language": language, "disposition": "eligible", "reason": kind,
    }


def analysis_args(inventory: Path, **overrides: object) -> argparse.Namespace:
    values = {
        "inventory": inventory, "output": None, "mode": "full", "scope": [], "checkpoint": None,
        "requirements": "required", "specifications": "none", "dashboard": "disabled", "max_concurrency": 4,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def semantic_totals(state: dict) -> dict[str, int]:
    names = (
        "flows", "business_rules", "data_structures", "dependencies", "interfaces",
        "defect_candidates", "unknowns",
    )
    return {
        name: sum(int(item.get("semantic_counts", {}).get(name, 0)) for item in state["coverage"]["artifacts"])
        for name in names
    }


def main() -> int:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        (root / "client_input").mkdir()
        (root / "analysis/canonical").mkdir(parents=True)
        source_text = {
            "request.cbl": ("MOVE REQUEST-ID TO HOST-ID.\nIF REQUEST-ID = SPACES GO TO INVALID-REQUEST.\n" * 900),
            "request.pli": ("IF REQUEST_ID = '' THEN SIGNAL INVALID_REQUEST;\nCALL HOST_SERVICE;\n" * 850),
            "Resource.java": ("if (request.id().isBlank()) throw new InvalidRequest();\nservice.call(request);\n" * 800),
            "request.cpy": ("05 REQUEST-ID PIC X(20).\n05 REQUEST-TYPE PIC X.\n" * 300),
            "service.yaml": ("operationId: submitRequest\nresponses:\n  '400': {description: invalid request}\n" * 250),
        }
        for name, source in source_text.items():
            (root / "client_input" / name).write_text(source, encoding="utf-8")
        for name in ("cobol.json", "pli.json", "java.json", "flow.json"):
            (root / "analysis/canonical" / name).write_text(
                json.dumps({"id": name, "observations": ["verified"] * 80}) + "\n", encoding="utf-8",
            )

        inventory = {
            "schema_version": 1,
            "root": "client_input",
            "fingerprint": "mixed-inventory-v1",
            "counts": {"files": 5, "eligible": 5, "failures": 0},
            "artifacts": [
                artifact("ART-CBL", "client_input/request.cbl", "cobol", digest(source_text["request.cbl"])),
                artifact("ART-PLI", "client_input/request.pli", "pli", digest(source_text["request.pli"])),
                artifact("ART-JAVA", "client_input/Resource.java", "java", digest(source_text["Resource.java"])),
                artifact("ART-COPY", "client_input/request.cpy", "copybook", digest(source_text["request.cpy"])),
                artifact("ART-API", "client_input/service.yaml", "yaml", digest(source_text["service.yaml"]), "configuration"),
            ],
            "batches": [], "failures": [],
        }
        inventory_path = root / "analysis/source-inventory.json"
        inventory_path.write_text(json.dumps(inventory, indent=2), encoding="utf-8")

        memory.initialize_memory(root, {
            "goal": "Reconstruct and modernize the request flow",
            "mode": "legacy-migration",
            "source_roots": ["client_input"],
            "protected_paths": ["client_input"],
            "target_technology": ["Java 21", "Spring Boot"],
            "languages": ["COBOL", "PL/I", "Java"],
            "architecture": "Equivalent request implementations sharing one contract and data layout",
            "lifecycle_stage": "analysis",
            "major_decisions": [], "critical_blockers": [],
            "next_action": "Resume the remaining COBOL validation review",
        })
        records = []
        for identifier, domain, entity, entity_type, statement, source, canonical in (
            ("COMP-CBL", "cobol", "REQUEST", "COBOL_PROGRAM", "COBOL validates and calls the host service.", "request.cbl", "cobol.json"),
            ("COMP-PLI", "pli", "REQUEST", "PLI_PROGRAM", "PL/I validates and calls the host service.", "request.pli", "pli.json"),
            ("COMP-JAVA", "java-api", "Resource", "JAVA_CLASS", "Java exposes the request API and validation.", "Resource.java", "java.json"),
        ):
            records.append({
                "id": identifier, "layer": "L2", "domain": domain,
                "entity": {"id": entity, "type": entity_type}, "statement": statement, "confidence": "VERIFIED",
                "canonical_refs": [{"path": f"analysis/canonical/{canonical}"}],
                "evidence": [{"path": f"client_input/{source}", "sha256": digest(source_text[source])}],
                "relationships": [{"type": "PARTICIPATES_IN", "target": "FLOW-REQUEST"}], "tags": ["request"],
            })
        records.append({
            "id": "FLOW-REQUEST", "layer": "L2", "domain": "flows",
            "entity": {"id": "REQUEST-FLOW", "type": "BUSINESS_FLOW"},
            "statement": "COBOL, PL/I, and Java implement the request flow with one known validation divergence.",
            "confidence": "VERIFIED", "canonical_refs": [{"path": "analysis/canonical/flow.json"}],
            "evidence": [
                {"path": "client_input/request.cbl", "sha256": digest(source_text["request.cbl"])},
                {"path": "client_input/request.pli", "sha256": digest(source_text["request.pli"])},
                {"path": "client_input/Resource.java", "sha256": digest(source_text["Resource.java"])},
            ],
            "relationships": [], "tags": ["cross-language", "divergence"],
        })
        memory.merge_proposal(root, {
            "schema_version": 1,
            "producer": {"id": "mixed-language-synthesis", "validation_status": "PASS"},
            "domains": [
                {"id": "cobol", "summary": "Deep COBOL request analysis."},
                {"id": "pli", "summary": "Deep PL/I request analysis."},
                {"id": "java-api", "summary": "Deep Java/API request analysis."},
                {"id": "flows", "summary": "Cross-language equivalence and divergence."},
            ],
            "records": records,
            "checkpoint": {"id": "LANGUAGE_ANALYSIS_COMPLETE", "status": "VALIDATED", "canonical_refs": [{"path": "analysis/canonical/flow.json"}]},
        })
        package = memory.build_context_package(root, {
            "task": "resume-cobol-validation", "domains": ["cobol"], "entities": ["REQUEST"],
            "dependency_depth": 1, "max_records": 20,
        })

        baseline_paths = [
            *[f"client_input/{name}" for name in source_text],
            *[f"analysis/canonical/{name}" for name in ("cobol.json", "pli.json", "java.json", "flow.json")],
            "analysis/source-inventory.json",
        ]
        baseline_bytes = sum((root / path).stat().st_size for path in baseline_paths)
        package_bytes = len(json.dumps(package, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))
        optimized_bytes = package_bytes + inventory_path.stat().st_size
        repetitions = 100
        started = time.perf_counter()
        for _ in range(repetitions):
            for path in baseline_paths:
                (root / path).read_bytes()
        baseline_runtime = time.perf_counter() - started
        started = time.perf_counter()
        for _ in range(repetitions):
            json.dumps(package, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
            inventory_path.read_bytes()
        optimized_runtime = time.perf_counter() - started

        checkpoint = coordinator.plan_state(analysis_args(inventory_path))
        for record in checkpoint["coverage"]["artifacts"]:
            if not record["assigned_slice"]:
                continue
            critical = record["language_type"] in {"cobol", "pli", "java"}
            evidence_id = "EVID-" + record["artifact_id"]
            record.update({
                "status": "ANALYZED", "evidence_ids": [evidence_id],
                "related_requirements": [], "reason": None,
                "depth_status": "DEEP_VERIFIED" if critical else "ANALYZED",
                "depth_dimensions": {
                    name: {"status": "VERIFIED", "evidence_ids": [evidence_id]}
                    for name in coordinator.DEPTH_DIMENSIONS
                },
                "semantic_counts": {
                    "flows": 3 if critical else 0,
                    "business_rules": 4 if critical else 0,
                    "data_structures": 2 if critical else 1,
                    "dependencies": 2 if critical else 1,
                    "interfaces": 1,
                    "defect_candidates": 1 if critical else 0,
                    "unknowns": 1 if critical else 0,
                },
                "complexity": [{"metric": "coupling", "basis": "ASSESSED", "value": "medium"}],
            })
        coordinator.recompute(checkpoint)
        checkpoint["lifecycle"]["synthesis"]["status"] = "VALIDATED"
        coordinator.recompute(checkpoint)
        checkpoint_path = root / "analysis/checkpoint.json"
        checkpoint_path.write_text(json.dumps(checkpoint), encoding="utf-8")
        source_reads: list[str] = []
        original_read_text = Path.read_text

        def measured_read_text(path: Path, *args: object, **kwargs: object) -> str:
            resolved = Path(path).resolve()
            try:
                relative = resolved.relative_to(root.resolve()).as_posix()
            except ValueError:
                relative = resolved.as_posix()
            if relative.startswith("client_input/"):
                source_reads.append(relative)
            return original_read_text(path, *args, **kwargs)

        with patch.object(Path, "read_text", measured_read_text):
            resumed = coordinator.plan_state(
                analysis_args(inventory_path, mode="continue", checkpoint=checkpoint_path)
            )

        before_quality = {
            "deep_verified_artifacts": checkpoint["coverage"]["summary"]["depth"]["deep_verified"],
            "semantic_findings": semantic_totals(checkpoint),
        }
        after_quality = {
            "deep_verified_artifacts": resumed["coverage"]["summary"]["depth"]["deep_verified"],
            "semantic_findings": semantic_totals(resumed),
        }
        payload = {
            "fixture": "mixed-cobol-pli-java",
            "measurement": "UTF-8 bytes",
            "baseline_no_optimized_memory": {
                "repeated_context_bytes": baseline_bytes,
                "repeated_source_reads": len(source_text),
                "repeated_inventory_payload_bytes": inventory_path.stat().st_size,
            },
            "optimized_memory": {
                "repeated_context_bytes": optimized_bytes,
                "context_package_bytes": package_bytes,
                "inventory_fingerprint_bytes": inventory_path.stat().st_size,
                "included_memory_records": package["metrics"]["included_records"],
                "available_memory_records": package["metrics"]["available_records"],
            },
            "context_reduction_percent": round((baseline_bytes - optimized_bytes) * 100.0 / baseline_bytes, 2),
            "performance": {
                "measurement_repetitions": repetitions,
                "baseline_runtime_seconds": round(baseline_runtime, 6),
                "optimized_runtime_seconds": round(optimized_runtime, 6),
                "runtime_change_percent": round((optimized_runtime - baseline_runtime) * 100.0 / baseline_runtime, 2),
                "tokens": "not_available"
            },
            "resume": {
                "validated_slices_reused": sum(item["status"] == "VALIDATED" for item in resumed["slices"]),
                "total_slices": len(resumed["slices"]),
                "repeated_unchanged_source_reads": len(source_reads),
                "read_measurement": "instrumented Path.read_text calls beneath client_input during continuation",
                "inventory_reused": resumed["inventory"]["fingerprint"] == checkpoint["inventory"]["fingerprint"],
            },
            "depth_quality": {
                "before": before_quality,
                "after": after_quality,
                "regression": before_quality != after_quality,
            },
            "limitations": [
                "This deterministic synthetic benchmark measures repeated UTF-8 payload bytes and state reuse, not runtime token billing.",
                "Measured runtime is environment-dependent and is reported as a trend, not a brittle pass threshold.",
            ],
        }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
