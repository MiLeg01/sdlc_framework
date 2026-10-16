# Mutation-quality benchmark and gate fixtures

Two kinds of fixture live here, and they are deliberately different in nature.

## `input/` and `benchmark-cases.json` — the executable benchmark

A synthetic invoice-totalling service with a reduced-rate threshold and a validated discount stands in for
REQ-017 and SPEC-004. Two suites target the same production code:

- `tax_calculator_weak_suite.py` — four tests, all passing, exercising only comfortable mid-range values;
- `tax_calculator_hardened_suite.py` — the same four tests plus the three behavioral tests that classified
  survivors demanded.

`benchmark-cases.json` declares five mutations with their operator, linked acceptance criterion, and expected
outcome per suite. `evals/tools/test_mutation_quality.py` executes them for real: it copies the fixture to a
temporary directory, applies one mutation, runs each suite, and records KILLED or SURVIVED. Nothing here is
asserted from a stored report.

### Measured before and after

Over the five declared mutants, with MUT-005 accepted as an equivalent mutant and therefore excluded from the
meaningful denominator:

| | Weak suite | Hardened suite |
| --- | --- | --- |
| Tests, all passing | 4 | 7 |
| Meaningful mutants | 4 | 4 |
| Killed | 1 (MUT-004) | 4 |
| Meaningful survivors | 3 (MUT-001, MUT-002, MUT-003) | 0 |
| Critical survivors | 3 | 0 |
| Mutation score | 25% | 100% |
| Accepted equivalent mutants | 1 (MUT-005) | 1 (MUT-005) |
| Gate | FAIL | PASS |

The point of the benchmark is the first row combined with the last. Both suites are entirely green, so a
passing-test signal cannot distinguish them. Mutation testing can: the weak suite never asserts the reduced-rate
boundary, the inclusive maximum discount rate, or the negative-rate rejection, so three financial-calculation
defects pass unnoticed. Each hardened test came from one classified survivor and asserts an acceptance
criterion, not an implementation detail. MUT-005 survives both suites and stays accepted, because killing it
would require asserting the evaluation order of two side-effect-free disjuncts, which no criterion requires.
This is why one hundred percent is not the target.

## `runs/` — normalized gate fixtures

These are normalized mutation runs in the contract defined by
`skills/mutation-testing/references/mutation-report-contract.md`, used to prove the deterministic gate. They
represent realistic tool output rather than runs produced here: this repository does not install PIT,
Stryker, or mutmut, so a full report from a real engine is out of scope for an offline evaluation. The
executable benchmark above is what provides genuine mutation evidence; these fixtures are what provide gate
coverage.

| Fixture | Proves |
| --- | --- |
| `strong-tests-run.json` | strong tests plus one justified equivalent mutant pass |
| `weak-tests-run.json` | critical survivors and a missed configured minimum fail |
| `non-critical-survivor-run.json` | non-critical survivors warn rather than fail |
| `unjustified-equivalence-run.json` | an equivalence claim without a reason stays in the denominator |
| `changed-scope-run.json` | changed-code scoping, and the changed-business-logic gate |
| `regressed-run.json` | a material regression against the accepted baseline fails |
| `flaky-baseline-run.json` | an unstable baseline blocks instead of scoring |
| `flaky-survivor-run.json` | an unreliable survivor result blocks the run |
| `failing-baseline-run.json` | a failing normal suite fails before mutation is interpreted |
| `invalid-execution-run.json` | invalid tool execution fails |
| `unsupported-technology-run.json` | an unsupported technology reports NOT_SUPPORTED, never a pass |
| `unclassified-survivor-run.json` | an unexamined survivor blocks the assessment |
| `policy.json`, `baseline.json` | the optional project policy and one accepted baseline |
