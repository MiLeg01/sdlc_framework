#!/usr/bin/env python3
"""Executable evaluations for external capability discovery and lifecycle mechanics."""

from __future__ import annotations

import argparse
import io
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import external_capabilities as external  # noqa: E402
import run_external_discovery as discovery_runner  # noqa: E402


SNAPSHOT = ROOT / "evals" / "fixtures" / "external" / "github-snapshot.json"
MODERNIZATION_SNAPSHOT = ROOT / "evals" / "fixtures" / "external" / "github-modernization-snapshot.json"


class ExternalCapabilityTests(unittest.TestCase):
    def search(self, topic: str, include_community: bool = False, trust: list[str] | None = None) -> dict[str, object]:
        return external.search(argparse.Namespace(
            sources=ROOT / "external" / "sources.yaml",
            topic=topic,
            project_root=None,
            source=["anthropic-official-plugins"],
            trust=trust or [],
            include_community=include_community,
            per_source_limit=4,
            community_limit=8,
            limit=20,
            snapshot=SNAPSHOT,
        ))

    def test_registry_and_reviewed_product_index_validate(self) -> None:
        registry = external.load_json(ROOT / "external" / "sources.yaml")
        index = external.load_json(ROOT / "external" / "index" / "capabilities.json")
        self.assertEqual([], external.validate_registry(registry))
        errors, warnings = external.validate_index(index, registry)
        self.assertEqual([], errors)
        self.assertEqual([], warnings)
        self.assertEqual(
            {
                "ext-github-community-discovery-footprintai-open-sdlc-skills",
                "ext-github-community-discovery-m-binimran-finance-pack",
            },
            {candidate["id"] for candidate in index["candidates"]},
        )
        self.assertTrue(all(candidate["status"] == "INCORPORATED" for candidate in index["candidates"]))
        self.assertTrue(all(candidate["relationship"] == "INSPIRED-BY" for candidate in index["candidates"]))

    def test_synthetic_revision_pinned_review_validates(self) -> None:
        headings = "\n\n".join(sorted(external.REVIEW_HEADINGS))
        review = """---
schema_version: 1
id: ext-synthetic-review
source_id: openai-official-skills
repository: openai/skills
path: skills/example
revision: 0000000000000000000000000000000000000000
trust: OFFICIAL
license: MIT
license_scope: LICENSE
security_class: INSTRUCTIONS ONLY
relationship: INDEPENDENT-REIMPLEMENTATION
status: REVIEWED
reviewed_at: 2026-08-19
---

# Synthetic external review

""" + headings + "\n"
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "review.md"
            path.write_text(review, encoding="utf-8")
            self.assertEqual([], external.validate_review(path))

    def test_github_url_normalization(self) -> None:
        expected = "anthropics/claude-plugins-official"
        self.assertEqual(expected, external.normalize_github("https://github.com/anthropics/claude-plugins-official.git"))
        self.assertEqual(expected, external.normalize_github("git@github.com:anthropics/claude-plugins-official.git"))

    def test_official_search_returns_high_trust_candidate(self) -> None:
        result = self.search("business rule extraction")
        candidate = result["candidates"][0]
        self.assertEqual("OFFICIAL", candidate["source_trust"])
        self.assertEqual("plugins/code-modernization", candidate["path"])
        self.assertEqual("3411fb9108778ca0e950db59c6511d2f7020cbc8", candidate["revision"])
        self.assertEqual("INSTRUCTIONS + SCRIPTS", candidate["security_class"])
        self.assertFalse(result["safety"]["installed"])
        self.assertFalse(result["safety"]["executed_external_code"])

    def test_hooks_and_remote_tooling_receive_stronger_security_classes(self) -> None:
        self.assertEqual(
            "PLUGIN WITH HOOKS",
            external.detect_security(["plugin/.claude-plugin/plugin.json", "plugin/hooks/preflight.py"]),
        )
        self.assertEqual(
            "MCP/REMOTE TOOLING",
            external.detect_security(["servers/example-mcp/index.ts"]),
        )

    def test_community_results_are_untrusted_and_low_signal_is_rejected(self) -> None:
        result = self.search("characterization testing", include_community=True)
        community = [candidate for candidate in result["candidates"] if candidate["source_trust"] == "COMMUNITY"]
        self.assertEqual(1, len(community))
        self.assertEqual("REVIEW", community[0]["review_recommendation"])

    def test_official_only_filter_excludes_requested_community_search(self) -> None:
        result = self.search("business rule extraction", include_community=True, trust=["OFFICIAL"])
        self.assertTrue(result["candidates"])
        self.assertTrue(all(candidate["source_trust"] == "OFFICIAL" for candidate in result["candidates"]))

    def test_direct_source_scope_overrides_conflicting_community_flag(self) -> None:
        args = argparse.Namespace(
            sources=ROOT / "external" / "sources.yaml", topic=["business rule extraction"],
            project_root=None, source=[], trust=[], include_community=True,
            per_source_limit=3, community_limit=8, limit=7, snapshot=MODERNIZATION_SNAPSHOT,
            cache_dir=None, cache_ttl_seconds=0, source_scope="official",
        )
        seen_trust: list[str] = []

        def configured(source, *_args):
            seen_trust.append(source["trust"])
            return []

        with mock.patch.object(external, "search_configured_source", side_effect=configured), \
                mock.patch.object(external, "community_results") as community:
            external.search(args)
        self.assertEqual(set(seen_trust), {"OFFICIAL"})
        community.assert_not_called()

    def test_no_useful_result_does_not_invent_value(self) -> None:
        result = self.search("COBOL target architecture")
        self.assertEqual([], result["candidates"])

    def test_configured_sources_are_scheduled_sequentially_to_respect_live_rate_budget(self) -> None:
        active = 0
        maximum = 0
        lock = threading.Lock()

        def fake_search(source, topics, client, snapshot, limit, cache_dir, cache_ttl):
            nonlocal active, maximum
            with lock:
                active += 1
                maximum = max(maximum, active)
            time.sleep(0.03)
            with lock:
                active -= 1
            return [{
                "id": f"ext-{source['id']}",
                "source_trust": source["trust"],
                "relevance_score": 10,
                "repository": source["repository"],
                "path": " | ".join(topics),
                "matched_gaps": list(topics),
                "review_recommendation": "REVIEW",
            }]

        arguments = argparse.Namespace(
            sources=ROOT / "external" / "sources.yaml",
            topic=["legacy modernization", "business rule extraction"],
            project_root=None,
            source=["anthropic-official-plugins", "openai-official-skills"],
            trust=[], include_community=False, per_source_limit=2,
            community_limit=2, limit=20, snapshot=SNAPSHOT, max_workers=4,
        )
        with mock.patch.object(external, "search_configured_source", side_effect=fake_search):
            result = external.search(arguments)
        self.assertEqual(maximum, 1)
        self.assertFalse(result["execution"]["parallel"])
        self.assertEqual(result["execution"]["configured_source_branches"], 2)
        self.assertEqual(result["execution"]["topics_scored_per_fetch"], 1)
        self.assertEqual(len(result["candidates"]), 2)

    def test_search_stops_after_enough_credible_candidates(self) -> None:
        def candidates(source, topics, client, snapshot, limit, cache_dir, cache_ttl):
            return [{
                "id": f"ext-{source['id']}-{index}", "source_trust": source["trust"],
                "relevance_score": 30, "repository": source["repository"], "path": f"skills/{index}",
                "matched_gaps": list(topics), "review_recommendation": "REVIEW",
            } for index in range(7)]

        arguments = argparse.Namespace(
            sources=ROOT / "external" / "sources.yaml", topic=["business rule extraction"], project_root=None,
            source=["anthropic-official-plugins", "openai-official-skills"], trust=[], include_community=True,
            per_source_limit=7, community_limit=8, limit=7, snapshot=SNAPSHOT,
            max_workers=1, cache_dir=None, cache_ttl_seconds=0,
        )
        with mock.patch.object(external, "search_configured_source", side_effect=candidates) as configured, \
             mock.patch.object(external, "community_results") as community:
            result = external.search(arguments)
        self.assertEqual(configured.call_count, 1)
        community.assert_not_called()
        self.assertTrue(result["execution"]["stopped_after_enough_candidates"])

    def test_recent_identical_search_reuses_cache(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            arguments = argparse.Namespace(
                sources=ROOT / "external" / "sources.yaml",
                topic=["business rule extraction"], project_root=None,
                source=["anthropic-official-plugins"], trust=[], include_community=False,
                per_source_limit=2, community_limit=2, limit=20, snapshot=SNAPSHOT,
                max_workers=2, cache_dir=Path(temporary), cache_ttl_seconds=300,
            )
            with mock.patch.object(external, "search_configured_source", wraps=external.search_configured_source) as search_source:
                first = external.search(arguments)
                second = external.search(arguments)
            self.assertFalse(first["cache"]["hit"])
            self.assertTrue(second["cache"]["hit"])
            self.assertEqual(search_source.call_count, 1)
            self.assertEqual(first["candidates"], second["candidates"])

    def test_recent_negative_search_result_is_reused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            arguments = argparse.Namespace(
                sources=ROOT / "external" / "sources.yaml", topic=["COBOL target architecture"],
                project_root=None, source=["anthropic-official-plugins"], trust=[], include_community=False,
                per_source_limit=2, community_limit=2, limit=20, snapshot=SNAPSHOT,
                max_workers=1, cache_dir=Path(temporary), cache_ttl_seconds=300,
            )
            with mock.patch.object(external, "search_configured_source", wraps=external.search_configured_source) as search_source:
                first = external.search(arguments)
                second = external.search(arguments)
            self.assertEqual(first["candidates"], [])
            self.assertTrue(second["cache"]["hit"])
            self.assertTrue(second["cache"]["negative_entry"])
            self.assertEqual(search_source.call_count, 1)

    def test_rate_limit_is_classified_without_losing_partial_result_contract(self) -> None:
        error = urllib.error.HTTPError(
            "https://api.github.com/repos/example/repo", 429, "rate limited", {"Retry-After": "60"}, io.BytesIO(b'{"message":"slow down"}'),
        )
        with mock.patch("urllib.request.urlopen", side_effect=error), mock.patch("time.sleep") as sleeper:
            with self.assertRaises(external.ProviderRequestError) as raised:
                external.GitHubClient(max_attempts=3, backoff_seconds=0.01, detect_auth=False).request("/repos/example/repo")
        self.assertEqual(raised.exception.failure["rate_limit_category"], "secondary")
        sleeper.assert_not_called()

    def test_authenticated_github_cli_is_preferred_without_reading_or_exposing_token(self) -> None:
        authenticated = subprocess.CompletedProcess(["gh", "auth"], 0, "", "")
        api = subprocess.CompletedProcess(
            ["gh", "api"], 0,
            'HTTP/2.0 200 OK\nx-ratelimit-resource: core\nx-ratelimit-remaining: 4999\n\n{"ok":true}', "",
        )
        with mock.patch("shutil.which", return_value="/usr/bin/gh"), \
             mock.patch("subprocess.run", side_effect=[authenticated, api]) as runner, \
             mock.patch.dict(os.environ, {"GITHUB_TOKEN": "must-not-appear"}, clear=False):
            client = external.GitHubClient()
            payload = client.request("/rate_limit", operation="rate-limit-inspection")
        self.assertEqual(client.transport, "gh-cli")
        self.assertTrue(client.authenticated)
        self.assertEqual(payload, {"ok": True})
        self.assertNotIn("must-not-appear", json.dumps(client.access_summary()))
        self.assertIn("auth", " ".join(runner.call_args_list[0].args[0]))
        self.assertEqual(runner.call_args_list[1].args[0][:3], ["gh", "api", "--include"])

    def test_unauthenticated_low_budget_stops_before_search(self) -> None:
        client = external.GitHubClient(detect_auth=False, minimum_remaining=3)
        client.observe_rate_limit({"X-RateLimit-Resource": "search", "X-RateLimit-Remaining": "2", "X-RateLimit-Reset": "1893456000"})
        self.assertFalse(client.can_schedule("repository-search"))
        failure = client.rate_limit_failure("repository-search")
        self.assertEqual(failure["rate_limit_category"], "primary")
        self.assertEqual(failure["remaining"], 2)
        self.assertNotIn("url", failure)

    def test_overlapping_topics_are_normalized_and_deduplicated(self) -> None:
        self.assertEqual(
            ["cobol migration", "pl/i semantic analysis", "spring boot 4.x migration"],
            external.normalize_topics([
                " COBOL   Migration ", "cobol modernization", "PL1 semantic analysis",
                "PL/I semantic analysis", "Java migration", "Spring Boot 4.x migration",
            ]),
        )

    def test_manual_topics_reject_unapproved_business_identifiers(self) -> None:
        with self.assertRaises(external.ExternalCapabilityError):
            external.validate_topic_privacy(["Acme claims adjudication business rules"])
        external.validate_topic_privacy(["COBOL to Java 21/Spring Boot 4.x migration mapping workflow"])

    def test_capability_matching_requires_more_than_one_generic_semantic_word(self) -> None:
        self.assertEqual(
            [],
            external.matched_capability_gaps(
                "COBOL business directory and company listings",
                ["COBOL business rule extraction"],
            ),
        )

    def test_partial_cache_entry_is_reused_without_new_search(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            arguments = argparse.Namespace(
                sources=ROOT / "external" / "sources.yaml", topic=["business rule extraction"],
                project_root=None, source=["anthropic-official-plugins"], trust=[], include_community=True,
                per_source_limit=2, community_limit=2, limit=5, snapshot=MODERNIZATION_SNAPSHOT,
                max_workers=1, cache_dir=Path(temporary), cache_ttl_seconds=300,
            )
            failure = external.ProviderRequestError({
                "provider": "github", "operation": "repository-search", "http_status": 403,
                "category": "rate-limit", "rate_limit_category": "primary", "remaining": 0,
                "reset_at": "2030-01-01T00:00:00Z", "retry_after_seconds": None,
                "cached_results_used": False,
            })
            with mock.patch.object(external, "community_results", side_effect=failure) as community:
                first = external.search(arguments)
                second = external.search(arguments)
            self.assertEqual(first["status"], "partial-rate-limited")
            self.assertTrue(second["cache"]["hit"])
            self.assertTrue(second["cache"]["partial_entry"])
            self.assertEqual(community.call_count, 1)

    def test_project_lease_prevents_concurrent_duplicate_searches(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "external-discovery.lock"
            first = external.DiscoveryLease(path, "same-request", stale_seconds=60)
            second = external.DiscoveryLease(path, "same-request", stale_seconds=60)
            self.assertTrue(first.acquire())
            self.assertFalse(second.acquire())
            first.release()
            self.assertTrue(second.acquire())
            second.release()

    def test_primary_and_secondary_403_and_429_are_structured_and_not_retried(self) -> None:
        cases = [
            (403, {"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "1893456000"}, b'{"message":"API rate limit exceeded"}', "primary"),
            (403, {"Retry-After": "120", "X-RateLimit-Remaining": "42"}, b'{"message":"secondary rate limit"}', "secondary"),
            (429, {"Retry-After": "60"}, b'{"message":"slow down"}', "secondary"),
        ]
        for status, headers, body, category in cases:
            with self.subTest(status=status, category=category):
                error = urllib.error.HTTPError("https://api.github.com/search/repositories?q=secret", status, "blocked", headers, io.BytesIO(body))
                client = external.GitHubClient(max_attempts=3, backoff_seconds=0.01, detect_auth=False)
                with mock.patch("urllib.request.urlopen", side_effect=error) as opener, mock.patch("time.sleep") as sleeper:
                    with self.assertRaises(external.ProviderRequestError) as raised:
                        client.request("/search/repositories?q=secret", operation="repository-search")
                record = raised.exception.failure
                self.assertEqual(record["http_status"], status)
                self.assertEqual(record["rate_limit_category"], category)
                self.assertEqual(record["remaining"], int(headers["X-RateLimit-Remaining"]) if "X-RateLimit-Remaining" in headers else None)
                self.assertEqual(record["retry_after_seconds"], int(headers["Retry-After"]) if "Retry-After" in headers else None)
                self.assertEqual(record["reset_at"], "2030-01-01T00:00:00Z" if "X-RateLimit-Reset" in headers else None)
                self.assertEqual(opener.call_count, 1)
                sleeper.assert_not_called()
                self.assertNotIn("secret", json.dumps(record))

    def test_secondary_limit_reset_blocks_follow_up_requests_without_retry_after(self) -> None:
        headers = {"X-RateLimit-Remaining": "42", "X-RateLimit-Reset": "1893456000"}
        error = urllib.error.HTTPError(
            "https://api.github.com/search/repositories?q=redacted", 403, "blocked", headers,
            io.BytesIO(b'{"message":"secondary rate limit"}'),
        )
        client = external.GitHubClient(detect_auth=False)
        with mock.patch("urllib.request.urlopen", side_effect=error):
            with self.assertRaises(external.ProviderRequestError):
                client.request("/search/repositories?q=redacted", operation="repository-search")
        self.assertFalse(client.can_schedule("repository-search"))

    def test_rate_limited_community_does_not_invalidate_official_results(self) -> None:
        arguments = argparse.Namespace(
            sources=ROOT / "external" / "sources.yaml", topic=["business rule extraction"],
            project_root=None, source=["anthropic-official-plugins"], trust=[], include_community=True,
            per_source_limit=3, community_limit=8, limit=7, snapshot=MODERNIZATION_SNAPSHOT,
            max_workers=1, cache_dir=None, cache_ttl_seconds=0,
        )
        failure = external.ProviderRequestError({
            "provider": "github", "operation": "repository-search", "http_status": 403,
            "category": "rate-limit", "rate_limit_category": "secondary", "remaining": 20,
            "reset_at": None, "retry_after_seconds": 90, "cached_results_used": False,
        })
        with mock.patch.object(external, "community_results", side_effect=failure):
            result = external.search(arguments)
        self.assertEqual(result["status"], "partial-rate-limited")
        self.assertTrue(any(candidate["source_trust"] == "OFFICIAL" for candidate in result["candidates"]))
        self.assertIn("OFFICIAL", result["completed_source_tiers"])
        self.assertNotIn("COMMUNITY", result["completed_source_tiers"])

    def test_offline_snapshot_uses_zero_network_requests(self) -> None:
        arguments = argparse.Namespace(
            sources=ROOT / "external" / "sources.yaml",
            topic=["COBOL semantic analysis", "PL/I business rule extraction", "Java 21 Spring Boot 4.x migration mapping"],
            project_root=None, source=["anthropic-official-plugins"], trust=[], include_community=True,
            per_source_limit=3, community_limit=8, limit=7, snapshot=MODERNIZATION_SNAPSHOT,
            max_workers=1, cache_dir=None, cache_ttl_seconds=0,
        )
        with mock.patch.object(external.GitHubClient, "request", side_effect=AssertionError("network used")):
            result = external.search(arguments)
        self.assertEqual(result["execution"]["network_requests"], 0)
        self.assertTrue(result["offline_snapshot"])
        self.assertTrue(all(not candidate["repository"].startswith("noise/") for candidate in result["candidates"]))

    def test_missing_mainframe_specific_capability_is_reported_explicitly(self) -> None:
        arguments = argparse.Namespace(
            sources=ROOT / "external" / "sources.yaml", topic=["COBOL semantic analysis", "PL/I business rule extraction"],
            project_root=None, source=["anthropic-official-plugins"], trust=["OFFICIAL"], include_community=False,
            per_source_limit=3, community_limit=8, limit=7, snapshot=MODERNIZATION_SNAPSHOT,
            max_workers=1, cache_dir=None, cache_ttl_seconds=0,
        )
        result = external.search(arguments)
        self.assertIn("No COBOL-specific capability was found.", result["coverage_notes"])
        self.assertIn("No PL/I-specific capability was found.", result["coverage_notes"])

    def test_generic_keyword_overlap_is_not_retained_as_a_candidate(self) -> None:
        result = external.community_results(
            ["COBOL semantic analysis", "Java 21 Spring Boot 4.x migration mapping"],
            external.GitHubClient(detect_auth=False), external.load_json(MODERNIZATION_SNAPSHOT), 10,
        )
        repositories = {candidate["repository"] for candidate in result}
        self.assertIn("specialists/mainframe-capability", repositories)
        self.assertNotIn("noise/java-migration-testing", repositories)
        self.assertTrue(all(candidate["matched_gaps"] for candidate in result))

    def test_compatible_topics_use_one_community_repository_search(self) -> None:
        client = external.GitHubClient(detect_auth=False)
        with mock.patch.object(client, "search_repositories", return_value=[]) as repository_search:
            result = external.community_results(
                ["COBOL semantic analysis", "PL/I business rule extraction", "Java 21 Spring Boot 4.x migration mapping"],
                client, None, 10,
            )
        self.assertEqual([], result)
        self.assertEqual(repository_search.call_count, 1)
        query = repository_search.call_args.args[0]
        self.assertIn("cobol semantic analysis", query)
        self.assertIn("pli business rule extraction", query)
        self.assertNotIn("analysis cobol semantic", query)

    def test_only_retained_community_candidates_are_revision_pinned(self) -> None:
        client = mock.Mock()
        client.search_repositories.return_value = [
            {
                "full_name": f"example/cobol-analysis-{index}",
                "description": "COBOL semantic analysis workflow",
                "default_branch": "main",
                "license": {"spdx_id": "MIT"},
                "stargazers_count": 100 - index,
                "updated_at": "2026-08-01T00:00:00Z",
            }
            for index in range(6)
        ]
        client.revision.return_value = ("a" * 40, "2026-08-01T00:00:00Z")
        results = external.community_results(
            ["COBOL semantic analysis"], client, None, limit=6, retain_limit=2,
        )
        self.assertEqual(len(results), 2)
        self.assertEqual(client.revision.call_count, 2)

    def test_community_revision_rate_limit_keeps_candidates_and_surfaces_partial_status(self) -> None:
        client = external.GitHubClient(detect_auth=False)
        item = {
            "full_name": "example/cobol-analysis", "description": "COBOL semantic analysis workflow",
            "default_branch": "main", "license": {"spdx_id": "MIT"}, "stargazers_count": 100,
            "updated_at": "2026-08-01T00:00:00Z",
        }
        failure = external.ProviderRequestError({
            "provider": "github", "operation": "repository-revision", "http_status": 403,
            "category": "rate-limit", "rate_limit_category": "secondary", "remaining": 10,
            "reset_at": "2030-01-01T00:00:00Z", "retry_after_seconds": 60,
            "cached_results_used": False,
        })
        with mock.patch.object(client, "inspect_rate_limit"), \
                mock.patch.object(client, "search_repositories", return_value=[item]), \
                mock.patch.object(client, "revision", side_effect=failure) as revision:
            result = external.search(argparse.Namespace(
                sources=ROOT / "external" / "sources.yaml", topic=["COBOL semantic analysis"],
                project_root=None, source=[], trust=["COMMUNITY"], include_community=True,
                per_source_limit=3, community_limit=8, limit=7, snapshot=None,
                cache_dir=None, cache_ttl_seconds=0, source_scope="all",
            ), client=client)
        self.assertEqual(result["status"], "partial-rate-limited")
        self.assertEqual(result["candidate_count"], 1)
        self.assertEqual(revision.call_count, 1)
        self.assertEqual(result["failures"][0]["operation"], "repository-revision")
        self.assertFalse(result["failures"][0]["cached_results_used"])
        self.assertNotIn("_default_branch", result["candidates"][0])
        self.assertNotIn("COMMUNITY", result["completed_source_tiers"])

    def test_rate_limit_inspection_keeps_repository_and_code_search_budgets_separate(self) -> None:
        client = external.GitHubClient(detect_auth=False, minimum_remaining=2)
        payload = {
            "resources": {
                "core": {"remaining": 100, "reset": 1893456000},
                "search": {"remaining": 1, "reset": 1893456000},
                "code_search": {"remaining": 20, "reset": 1893456000},
            },
        }
        with mock.patch.object(client, "request", return_value=payload):
            client.inspect_rate_limit()
        self.assertFalse(client.can_schedule("repository-search"))
        self.assertTrue(client.can_schedule("code-search"))

    def test_failed_cache_entry_is_not_reused_and_cache_hit_reports_zero_requests(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            args = argparse.Namespace(
                sources=ROOT / "external" / "sources.yaml", topic=["COBOL semantic analysis"],
                project_root=None, source=[], trust=["COMMUNITY"], include_community=True,
                per_source_limit=3, community_limit=8, limit=7, snapshot=MODERNIZATION_SNAPSHOT,
                cache_dir=Path(temporary), cache_ttl_seconds=300, source_scope="all",
            )
            registry = external.load_json(args.sources)
            topics = external.normalize_topics(args.topic)
            revision = external.source_revision_fingerprint(args, registry, external.load_json(args.snapshot))
            path = Path(temporary) / f"{external.search_cache_key(args, registry, topics, revision)}.json"
            failed = {
                "schema_version": 2, "status": "failed", "candidates": [], "failures": [],
                "execution": {"network_requests": 4},
            }
            path.write_text(json.dumps(failed), encoding="utf-8")
            cached, _ = external.cached_search(args, registry, topics, revision)
            self.assertIsNone(cached)
            failed["status"] = "partial-rate-limited"
            failed["candidates"] = [{"id": "retained"}]
            path.write_text(json.dumps(failed), encoding="utf-8")
            cached, _ = external.cached_search(args, registry, topics, revision)
            self.assertIsNotNone(cached)
            self.assertEqual(cached["execution"]["network_requests"], 0)
            self.assertEqual(cached["execution"]["cached_entry_network_requests"], 4)

    def test_cache_identity_changes_with_snapshot_source_revision(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first_snapshot = root / "first.json"
            second_snapshot = root / "second.json"
            payload = external.load_json(MODERNIZATION_SNAPSHOT)
            first_snapshot.write_text(json.dumps(payload), encoding="utf-8")
            payload["repositories"]["anthropics/claude-plugins-official"]["revision"] = "d" * 40
            second_snapshot.write_text(json.dumps(payload), encoding="utf-8")
            base = dict(
                sources=ROOT / "external" / "sources.yaml", topic=["business rule extraction"],
                project_root=None, source=["anthropic-official-plugins"], trust=[], include_community=False,
                per_source_limit=3, community_limit=8, limit=7, cache_dir=root, cache_ttl_seconds=300,
            )
            first_args = argparse.Namespace(**base, snapshot=first_snapshot)
            second_args = argparse.Namespace(**base, snapshot=second_snapshot)
            registry = external.load_json(first_args.sources)
            first_revision = external.source_revision_fingerprint(first_args, registry, external.load_json(first_snapshot))
            second_revision = external.source_revision_fingerprint(second_args, registry, external.load_json(second_snapshot))
            self.assertNotEqual(
                external.search_cache_key(first_args, registry, first_args.topic, first_revision),
                external.search_cache_key(second_args, registry, second_args.topic, second_revision),
            )

    def test_repository_evidence_cache_avoids_repeat_metadata_tree_requests(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            client = mock.Mock()
            client.repository.return_value = {"full_name": "example/repo", "default_branch": "main", "license": {"spdx_id": "MIT"}}
            client.revision.return_value = ("a" * 40, "2026-08-01T00:00:00Z")
            client.tree.return_value = ["skills/example/SKILL.md"]
            first = external.repository_evidence("example/repo", client, None, Path(temporary), 300)
            second = external.repository_evidence("example/repo", client, None, Path(temporary), 300)
            self.assertEqual(first["revision"], second["revision"])
            self.assertTrue(second["_cache_hit"])
            self.assertEqual(client.repository.call_count, 1)
            self.assertEqual(client.revision.call_count, 1)
            self.assertEqual(client.tree.call_count, 1)

    def test_zero_live_budget_still_uses_fresh_official_repository_cache(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            cache_dir = Path(temporary)
            snapshot = external.load_json(MODERNIZATION_SNAPSHOT)
            evidence = snapshot["repositories"]["anthropics/claude-plugins-official"]
            external.store_repository_evidence(cache_dir, "anthropics/claude-plugins-official", evidence)
            client = external.GitHubClient(detect_auth=False, minimum_remaining=2)
            client.observe_rate_limit({
                "X-RateLimit-Resource": "core", "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": "1893456000",
            })
            with mock.patch.object(client, "inspect_rate_limit"), mock.patch.object(client, "repository") as repository:
                result = external.search(argparse.Namespace(
                    sources=ROOT / "external" / "sources.yaml", topic=["business rule extraction"],
                    project_root=None, source=["anthropic-official-plugins"], trust=[], include_community=False,
                    per_source_limit=3, community_limit=8, limit=7, snapshot=None,
                    cache_dir=cache_dir, cache_ttl_seconds=0, repository_cache_ttl_seconds=300,
                    source_scope="official",
                ), client=client)
            self.assertEqual(result["status"], "completed")
            self.assertEqual(result["candidate_count"], 1)
            self.assertTrue(result["candidates"][0]["repository_metadata_cache_hit"])
            repository.assert_not_called()

    def test_persisted_rate_limit_failure_is_structured_and_redacted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            state = root / ".agent-commons/external-discovery.json"
            output = root / "analysis/external-capabilities.json"
            args = argparse.Namespace(
                project_root=root, state=state, output=output, topic=["COBOL semantic analysis"],
                gap=["cobol-semantic-analysis"], source_scope="all",
                sources=ROOT / "external" / "sources.yaml", snapshot=MODERNIZATION_SNAPSHOT,
                cache_dir=root / "cache", cache_ttl_seconds=300, repository_cache_ttl_seconds=300,
                lock=None, lease_stale_seconds=300,
            )
            failure = {
                "provider": "github", "operation": "repository-search", "http_status": 403,
                "category": "rate-limit", "rate_limit_category": "primary", "remaining": 0,
                "reset_at": "2030-01-01T00:00:00Z", "retry_after_seconds": None,
                "cached_results_used": True,
            }
            search_result = {
                "schema_version": 2, "status": "partial-rate-limited", "candidates": [{"id": "retained"}],
                "failures": [failure], "completed_source_tiers": ["OFFICIAL"],
                "source_tiers": {"OFFICIAL": {"status": "completed"}}, "cache": {"hit": False},
                "safety": {"installed": False, "executed_external_code": False, "mutated_commons": False},
            }
            with mock.patch.object(discovery_runner.external_capabilities, "search", return_value=search_result):
                self.assertEqual(discovery_runner.run(args), 0)
            persisted = json.loads(state.read_text(encoding="utf-8"))
            self.assertEqual(persisted["status"], "partial-rate-limited")
            self.assertEqual(persisted["candidate_count"], 1)
            self.assertEqual(persisted["completed_source_tiers"], ["OFFICIAL"])
            self.assertEqual(persisted["failures"], [failure])
            self.assertNotIn("url", json.dumps(persisted).casefold())
            self.assertEqual(persisted["safety"], search_result["safety"])

    def test_runner_records_lock_contention_instead_of_leaving_running_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            state = root / ".agent-commons/external-discovery.json"
            output = root / "analysis/external-capabilities.json"
            args = argparse.Namespace(
                project_root=root, state=state, output=output, topic=["COBOL semantic analysis"],
                gap=["cobol-semantic-analysis"], source_scope="all",
                sources=ROOT / "external" / "sources.yaml", snapshot=MODERNIZATION_SNAPSHOT,
                cache_dir=root / "cache", cache_ttl_seconds=300, repository_cache_ttl_seconds=300,
                lock=None, lease_stale_seconds=300,
            )
            request_key = external.discovery_request_key(args.topic, args.source_scope, args.sources, args.snapshot)
            state.parent.mkdir(parents=True, exist_ok=True)
            state.write_text(json.dumps({"status": "running", "request_key": request_key}), encoding="utf-8")
            lease = external.DiscoveryLease(state.parent / "external-discovery.lock", request_key, 300)
            self.assertTrue(lease.acquire())
            try:
                self.assertEqual(discovery_runner.run(args), 0)
            finally:
                lease.release()
            persisted = json.loads(state.read_text(encoding="utf-8"))
            self.assertEqual(persisted["status"], "failed")
            self.assertEqual(persisted["failures"][0]["category"], "lock-contention")

    def test_cobol_pli_legacy_java_to_java21_spring4_scenario(self) -> None:
        arguments = argparse.Namespace(
            sources=ROOT / "external" / "sources.yaml",
            topic=[
                "COBOL semantic analysis", "COBOL migration", "PL1 business rule extraction",
                "PL/I business rule extraction", "legacy Java migration",
                "Java 21 Spring Boot 4.x migration mapping",
            ],
            project_root=None, source=["anthropic-official-plugins"], trust=[], include_community=True,
            per_source_limit=3, community_limit=8, limit=7, snapshot=MODERNIZATION_SNAPSHOT,
            max_workers=1, cache_dir=None, cache_ttl_seconds=0,
        )
        result = external.search(arguments)
        repositories = {candidate["repository"] for candidate in result["candidates"]}
        self.assertEqual(result["status"], "completed")
        self.assertIn("specialists/mainframe-capability", repositories)
        self.assertIn("specialists/java21-spring4-modernizer", repositories)
        self.assertNotIn("noise/java-migration-testing", repositories)
        self.assertEqual(result["candidate_count"], len(result["candidates"]))
        self.assertEqual(result["execution"]["network_requests"], 0)
        self.assertEqual(result["coverage_notes"], [])
        self.assertEqual(result["safety"], {
            "installed": False, "executed_external_code": False, "mutated_commons": False,
        })

    def test_project_query_excludes_client_and_goal_details(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / ".agent-commons.yaml").write_text(
                'project:\n  name: "Secret Client Apollo"\n  goal: "Rebuild internal claims engine"\n  scopes:\n    - legacy-migration\ncommons:\n  skills:\n    - audit-delivery-traceability\n',
                encoding="utf-8",
            )
            (root / "Application.java").write_text("class Application {}\n", encoding="utf-8")
            result = external.project_query(root)
            encoded = json.dumps(result)
            self.assertNotIn("Secret Client Apollo", encoded)
            self.assertNotIn("claims engine", encoded)
            self.assertIn("Java", result["signals"]["technologies"])
            self.assertIn("legacy modernization", result["terms"])

    def test_sensitive_manual_topics_are_rejected_before_provider_access(self) -> None:
        for topic in (
            "client: Secret Client COBOL migration",
            "inspect /Users/example/private-repo for migration tools",
            "search private-owner/private-repository for testing",
        ):
            with self.subTest(topic=topic):
                arguments = argparse.Namespace(
                    sources=ROOT / "external" / "sources.yaml", topic=[topic], project_root=None,
                    source=[], trust=[], include_community=True, per_source_limit=3,
                    community_limit=8, limit=7, snapshot=None, cache_dir=None, cache_ttl_seconds=0,
                )
                with mock.patch.object(external.GitHubClient, "request") as request:
                    with self.assertRaises(external.ExternalCapabilityError):
                        external.search(arguments)
                request.assert_not_called()

    def test_project_query_uses_recorded_capability_gaps(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / ".agent-commons.yaml").write_text(
                'project:\n  scopes:\n    - legacy-migration\nmigration:\n  source_technology: "SAS"\n  target_technology: "Java"\ncapability_state:\n  gaps:\n    - id: "sas-semantic-analysis"\n      status: MISSING\nexternal_capabilities:\n  accepted: []\n',
                encoding="utf-8",
            )
            result = external.project_query(root)
            self.assertIn("SAS code semantic analysis agent skill", result["terms"])
            self.assertIn("SAS to Java migration mapping workflow", result["terms"])
            self.assertEqual(["sas-semantic-analysis"], result["signals"]["capability_gaps"])

    def test_project_query_preserves_cobol_pli_and_java21_specific_gaps(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / ".agent-commons.yaml").write_text(
                'project:\n  name: "Private Client"\n  scopes:\n    - legacy-migration\n    - development\n'
                'migration:\n  target_technology: "Java 21 Spring Boot 4.x"\ncapability_state:\n  gaps: []\nexternal_capabilities:\n  accepted: []\n',
                encoding="utf-8",
            )
            (root / "program.cbl").write_text("IDENTIFICATION DIVISION.\n", encoding="utf-8")
            (root / "module.pli").write_text("PROC OPTIONS(MAIN);\n", encoding="utf-8")
            (root / "Legacy.java").write_text("class Legacy {}\n", encoding="utf-8")
            result = external.project_query(root)
            self.assertTrue(any(term.startswith("COBOL semantic") for term in result["terms"]))
            self.assertTrue(any(term.startswith("PL/I semantic") for term in result["terms"]))
            self.assertTrue(any("Java 21 Spring Boot 4.x" in term for term in result["terms"]))
            self.assertNotIn("Private Client", json.dumps(result))

    def test_stale_review_detected_without_overwriting_review(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            index_path = Path(temp) / "index.json"
            index = external.load_json(ROOT / "external" / "index" / "capabilities.json")
            index["candidates"] = [{
                "id": "ext-synthetic-stale-review",
                "repository": "anthropics/claude-plugins-official",
                "revision": "0000000000000000000000000000000000000000",
                "review_status": "CURRENT",
            }]
            index_path.write_text(json.dumps(index), encoding="utf-8")
            result = external.check_stale(argparse.Namespace(index=index_path, snapshot=SNAPSHOT, write=False))
            self.assertEqual("REVIEW OUTDATED", result["results"][0]["result"])
            self.assertFalse(result["reviews_overwritten"])


if __name__ == "__main__":
    unittest.main()
