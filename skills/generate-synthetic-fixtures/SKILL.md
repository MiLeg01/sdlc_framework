---
name: generate-synthetic-fixtures
description: Build committed test fixtures by generating them deterministically from a reviewed allowlist specification instead of scrubbing sensitive originals, keeping the behavioral signal tests depend on while every identity value is an approved synthetic one. Use when a suite needs realistic documents or records derived from sensitive material that will live in version control. Do not use to transform an existing structured dataset for analysis, to purge sensitive data already committed to history, or to sanitize prose.
---

# Generate synthetic fixtures

Tests need fixtures that look like the real thing. The obvious route — take a real artifact and remove what
is sensitive — fails in a way that is invisible: a missed field looks exactly like a clean file, and once
committed it is in history forever. Redaction is a denylist, and a denylist is only as good as the last
thing someone thought of.

Invert it. Generate the fixture from a specification that contains only approved values, so **the
specification is the audit surface**. Reviewing one small declarative file is a task a human can actually
complete; auditing a rendered artifact for what is missing is not.

## Boundaries

This workflow produces new artifacts. It never edits a sensitive original in place, and no byte of a
sensitive original reaches the committed fixture except through a value someone approved in the
specification.

Use `anonymize-data` instead when the input is a structured dataset that must retain analytical utility
and the field inventory is known and bounded. Use this workflow when the artifact is a document or record
whose value to the test is **behavioral signal** rather than data fidelity, and where a missed field would
not be visible on inspection. Sensitive data already committed to history is a separate authorized
operation and is out of scope here.

## Establish the specification

1. Extract the structure of the source artifact — its sections, ordering, labels, and vocabulary — and
   inventory every value that identifies a person, account, contract, device, or location. An
   extract-and-flag helper may surface candidates, but it proposes; it never writes the replacement.
2. Decide, value by value, which of two categories each one falls in, and record the decision:
   - **Identity** — replaced by an approved synthetic value. Names, account and policy numbers, national
     identifiers, addresses, contact details, dates of birth.
   - **Load-bearing signal** — kept verbatim because a test depends on it. Classification vocabulary,
     structural labels, public institution or product names that drive routing, and the exact values an
     assertion checks.
   Neither category is safe to guess. A kept value must be justified by a test that needs it; a replaced
   value must be approved rather than invented at render time.
3. Write the specification as declarative data: an approved-value set shared across fixtures, plus one
   entry per fixture naming its renderer, its classification labels, its content fields, and the tokens
   the test depends on. Keep it small enough to review in one sitting.
4. Detectors for structured identifier formats belong in this workflow as an **assertion over the
   generated output**, never as the transformation. Their job is to fail the build when an unapproved
   identifier-shaped value appears, not to find and remove sensitive data.

Values that are not format-detectable — personal names above all — are found by review, not by pattern.
Say so explicitly rather than implying the detectors are complete.

## Generate deterministically

The renderer must be a pure function of the specification. A clock, a random source, or any ambient state
inside a render path destroys reproducibility, and reproducibility is what makes the specification
authoritative rather than merely aspirational. Pin any renderer setting that would otherwise embed a
timestamp, identifier, or environment detail.

When a source artifact has no extractable structure — a scan, an image, an opaque binary — do not attempt
to derive from it. Author the specification from the artifact's *type* instead, and record that the entry
was authored rather than derived.

## Validate

Make the guarantees executable. Each is a distinct failure this workflow exists to prevent:

- **Reproducibility** — regenerating every fixture from the specification reproduces the committed artifact.
  A drifted fixture means someone edited the output instead of the specification.
- **Determinism** — two consecutive renders of the same entry are identical.
- **No unapproved identifiers** — the detectors find nothing outside the approved set in any committed
  fixture.
- **Declared parity** — the set of declared entries and the set of committed artifacts match exactly, in
  both directions, so neither an orphan artifact nor a phantom declaration survives.
- **Signal presence** — each fixture contains the tokens its test depends on, so a regeneration that
  silently drops load-bearing content fails here rather than as a confusing test failure later.

Run these as ordinary tests in the normal suite, not as a manual checklist.

## Completion and stop conditions

Complete when every fixture regenerates reproducibly, the validations pass, and every identity value in
the specification is one that was approved rather than carried over.

Stop and escalate rather than improvising when a required value cannot be classified as identity or
signal, when a test appears to depend on a real identifier, when no renderer fits the artifact and adding
one is out of scope, or when a source artifact would have to be edited in place to proceed. Do not weaken
a detector, widen the approved set, or commit an artifact to make a validation pass — each of those
converts a visible failure into an invisible one, which is the exact outcome this workflow exists to
prevent.
