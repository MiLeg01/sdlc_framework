# Commons review report contract

## Markdown report

Write `docs/commons-review.md` with this structure.

### Commons Review

Record sanitized root labels, inspection date, source scope, exclusions, and validation limits. Use `.` for
the current project and `<commons-root>` for the canonical library when real roots expose usernames,
clients, applications, or other private identifiers.

### Summary

Report reconciled counts for:

- new commons candidates;
- existing commons update candidates;
- replacement or deprecation candidates;
- local duplicates;
- intentionally project-local patterns;
- rejected candidates.

### Stable candidate IDs

Assign an immutable ID to every detailed entry:

- `P0-NNN` for high-confidence candidates ready for explicit promotion revalidation;
- `P1-NNN` for candidates that need more evidence or a decision;
- `DNP-NNN` for local, duplicate, unsafe, immature, or rejected candidates.

Use three-digit sequence numbers within each prefix. Preserve an existing candidate's ID when refreshing
the report, even if its priority changes; record the new priority separately rather than silently
renumbering it. IDs are selectors, not approval.

### New commons candidates

For each candidate include:

- stable candidate ID;
- candidate name and proposed type;
- project-relative source paths and observed-use evidence, with sensitive path segments redacted;
- reusable problem solved;
- required generalization and confidentiality scrub;
- commons capabilities compared and semantic overlap result;
- trigger and non-trigger;
- proposed commons location;
- confidence: `HIGH`, `MEDIUM`, or `LOW`;
- recommendation: `PROMOTE`, `INVESTIGATE`, or `KEEP_LOCAL`.

### Existing commons update candidates

For each candidate include:

- stable candidate ID;
- exact existing capability;
- project discovery and source evidence;
- concrete proposed improvement and rationale;
- compatibility impact;
- positive, negative, collision, and regression evals required;
- recommendation: `UPDATE`, `INVESTIGATE`, or `NO_CHANGE`.

### Replacement or deprecation candidates

Require strong evidence. State whether to replace, merge, split, or deprecate; identify the survivor or
replacement, migration impact, and required validation.

### Local duplicates

Identify project-local skills, agents, tools, or instructions already covered adequately by commons.
Recommend possible later cleanup, but do not delete anything.

### Intentionally project-local

Record interesting candidates that must remain local and why. Include enough reasoning to prevent repeated
reconsideration without exposing confidential content.

### Rejected candidates

Briefly record weak candidates and a reason such as too specific, duplicate, immature, speculative,
trivial, client-specific, obsolete, or insufficient benefit.

### Promotion plan

Organize actions into `P0`, `P1`, and `Do not promote`. For each P0 item specify:

```text
ACTION
ADD, UPDATE, MERGE, REPLACE, or DEPRECATE

COMMONS FILES
<likely canonical paths>

EVALS
<new or changed cases>

SOURCE EVIDENCE
<project paths>
```

These are proposed changes only.

## JSON report

Write `docs/commons-review.json` with this minimal shape:

```json
{
  "schema_version": 1,
  "project_root": ".",
  "commons_root": "<commons-root>",
  "generated_at": "<ISO-8601 timestamp>",
  "summary": {
    "new": 0,
    "updates": 0,
    "replacements": 0,
    "local_duplicates": 0,
    "project_local": 0,
    "rejected": 0
  },
  "new_candidates": [],
  "update_candidates": [],
  "replacement_candidates": [],
  "local_duplicates": [],
  "project_local_candidates": [],
  "rejected_candidates": []
}
```

Each entry should contain only concise identifiers, project-relative sanitized source paths, comparison
result, confidence, recommendation, and proposed commons paths where applicable. Do not duplicate the full
Markdown narrative.

Include `candidate_id` and `priority` in every entry. Stable IDs allow a later controlled promotion gate
to select one or more candidates without treating the review itself as approval.
