# Evidence-constrained migration contract

The manifest is JSON with `schemaVersion: "1.0.0"` and these sections:

- `source`: root, language, deterministic fingerprint, and `readOnly: true`;
- `target`: distinct isolated root, language, and accepted constraints;
- `scope`: explicit included and excluded boundaries;
- `safety`: external credentials, disabled-by-default network, isolated-target writes, and required human review;
- `slices`: stable ID, lifecycle status, source artifacts, requirements, acceptance scenarios, target artifacts,
  tests, and validation commands.

Allowed slice statuses are `PLANNED`, `RED`, `GREEN`, `VERIFIED`, and `BLOCKED`. Status is evidence, not a
percentage. A slice cannot become `VERIFIED` until source-to-scenario-to-test links resolve and the required
broader gates pass.

The validator rejects shared source and target roots, writable sources, embedded credential-like keys,
missing trace lists, unsafe shell commands, and weakened safety defaults. It validates the manifest contract;
it does not execute migration or prove semantic parity.
