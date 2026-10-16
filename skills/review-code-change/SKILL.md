---
name: review-code-change
description: Review a complete code or pull-request change with full diff coverage, local-standard checks, validation evidence, severity-ranked findings, and a separate factual change summary. Use for pre-merge review, consequential patches, or re-review after corrections. Do not use to implement the change while claiming independence, post comments externally without explicit authorization, or review only filenames and generated summaries.
---

# Review a code change

Review the actual change and its context. A summary explains what changed; findings explain what is wrong.

## Establish scope

1. Read repository instructions, review policy, relevant architecture and tests, existing review feedback,
   and the complete base-to-head diff including renames, deletions, generated files, and untracked work.
2. Identify intended behavior, acceptance evidence, affected callers, data or security boundaries, and
   validation already run.
3. Build a file checklist and account for every changed path. Treat generated output according to its
   canonical source and drift rules.

## Inspect

Trace changed behavior through callers, callees, configuration, persistence, concurrency, error paths,
authorization, privacy, compatibility, and user-visible states. Verify tests assert the intended behavior,
fail for meaningful reasons, cover boundaries, and do not hide regressions behind mocks or snapshots.
Use local standards and exact source evidence; do not invent style requirements.

## Report

Return:

1. a concise factual change summary and validation summary;
2. findings ordered by severity, each with a tight location, reproduction or concrete failure path, impact,
   evidence, and bounded correction direction;
3. unresolved questions, coverage limits, and an explicit no-findings statement when appropriate.

Prioritize correctness, security, data loss, broken contracts, and user-visible regressions over cosmetic
preference. Avoid praise, vague risk, duplicate findings, and issues outside the change unless the change
materially exposes them.

Keep review read-only. Drafting local findings is authorized by the review request; submitting comments,
approvals, status changes, or messages to an external system requires explicit confirmation. Re-review the
corrected diff and relevant validation before closing findings.
