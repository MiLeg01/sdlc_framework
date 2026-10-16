# Promotion report contract

Write one Markdown report under the repository's promotion-report directory. Use a date and short slug in
the filename when no stronger local convention exists.

## Required fields

Record:

- promotion ID and date;
- source review, audit, external review, or explicit source;
- exact user-selected and excluded candidates;
- per-candidate revalidation summary and disposition;
- promoted, blocked, and no-change candidates;
- created, updated, deprecated, and deleted files;
- evals added or changed;
- confidentiality scan result;
- external provenance and license result when relevant;
- provenance changes;
- adapter and runtime verification;
- catalog and relationship changes;
- archetype or overlay integration, including a reason when none is appropriate;
- documentation changes, deterministic presentation-refresh result, and narrative-impact recommendation;
- version and changelog result;
- validation commands and exact outcomes;
- commit identity or an explicit statement that the report is contained in that commit;
- remaining limitations and follow-up decisions.

## Candidate table

Use one row per selected candidate:

| Candidate | Selected by | Evidence | Overlap | Action | Disposition | Result |
|---|---|---|---|---|---|---|

Keep source paths sanitized. Separate observed evidence, interpretation, decisions, assumptions, conflicts,
and unknowns.

## Validation table

Use one row per command or bounded manual check:

| Validation | Result | Evidence or limit |
|---|---|---|

Do not convert an unavailable browser, runtime, license, or business acceptance surface into a pass.

## Final summary

End with actual counts and values:

```text
Selected: <count>
Promoted: <count>
Blocked: <count>
No change: <count>
Evals: <count added or changed>
Adapters: <verified runtimes or limits>
Validation: PASS or FAILED
Version: <before> -> <after, or unchanged>
Commit: <hash or exact pending reason>
```

If nothing should be promoted, say so directly and record the disposition. Do not invent a canonical
change to make the report look successful.
