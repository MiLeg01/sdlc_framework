---
name: anonymize-data
description: Design and apply bounded, configurable data anonymization or pseudonymization with field-scoped rules, deterministic local transforms, leakage-safe reports, and explicit residual-risk validation. Use before sharing structured sensitive data across a trust boundary. Do not use to claim legal anonymization, infer unknown identifiers from free text, or replace privacy review and data-minimization decisions.
---

# Anonymize data safely

Establish the authorized purpose, recipients, trust boundary, data classes, acceptable analytical utility,
retention, reversibility needs, and attack model. Minimize or exclude data before transforming it.

## Define the protection contract

1. Inventory the bounded input and classify direct identifiers, quasi-identifiers, sensitive attributes,
   linkage keys, free text, and fields that must retain analytical meaning.
2. Choose terminology honestly. Removal or irreversible aggregation may support anonymization; stable tokens
   and mapping-backed restoration are pseudonymization and remain personal-data controls in many contexts.
3. Define exact field selectors and one strategy per field: drop, fixed redaction, or keyed stable token.
   Do not detect people from capitalization, broad heuristics, or unreviewed regular expressions.
4. Set required rules for identifiers that must be present and protected. Define false-positive fixtures,
   multilingual examples, duplicates, aliases, empty values, and nested records.
5. Keep keys and optional restoration maps outside source, configuration, logs, reports, fixtures, and
   generated artifacts. Use separate access and retention controls for reversible mappings.

Use `references/rule-contract.md` for the portable configuration and validation contract.

## Execute locally and fail closed

For JSON, JSONL, NDJSON, or CSV, use `scripts/anonymize_data.py` against a copy or isolated output path.
Run `--dry-run` first, inspect match counts and digests, then write the transformed output. Stable tokens
require a separately supplied key file. The report contains counts and hashes, never matched source values.

Stop when required rules do not match, formats are malformed, field ownership is ambiguous, output would
overwrite input, a key is missing, or validation cannot inspect the complete outbound payload. Unsupported
binary documents and free text require an explicit extraction and review plan; do not silently downgrade.

## Verify the boundary

- Compare the complete outbound artifact against synthetic canaries and authorized identifier fixtures.
- Test positives, negatives, false positives, determinism, nesting, duplicates, multilingual values,
  unsupported formats, lifecycle cleanup, and default failure behavior.
- Confirm logs, errors, telemetry, backups, browser state, caches, reports, and test artifacts contain no
  protected source values or token keys.
- Measure retained utility and linkage risk separately. State residual risk and what was not tested.

For consequential use, delegate the completed evidence to `privacy-security-reviewer`. The reviewer remains
findings-only; the implementation owner applies approved changes and owns release decisions.
