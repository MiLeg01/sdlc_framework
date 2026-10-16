# Golden expectations

Golden files protect facts, invariants, required relationships, and critical failure conditions. They do not
store or compare complete generated prose. Representative project facts may be classified `CRITICAL`, `MAJOR`,
or `MINOR`; a missed `CRITICAL` fact hard-fails even when aggregate recall remains high.

Changes under this directory are protected evaluation changes. A changed-capability run fails unless the
caller explicitly supplies `--allow-protected-eval-changes`, and review must explain why the prior expectation
was incorrect or why an approved product decision changed it. Capability implementation changes and golden
changes should be reviewed separately whenever practical.

Validator-only expectations for representative projects live beside their fixtures under
`evals/fixtures/projects/<project>/golden/`. Those directories receive the same protected-change treatment and
must never appear in executor `source_artifacts`.
