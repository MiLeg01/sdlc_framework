# Mutation Testing and TDD Test Quality

This report records the canonical Agent Commons decision and validation evidence for first-class application
mutation testing. The purpose is not to check whether tests pass, but to determine whether they are strong
enough to detect meaningful defects in the implementation.

TDD asks: *did we specify behavior through tests?* Mutation testing asks: *would those tests fail if the
implementation were wrong?* Passing tests are not evidence of high-quality tests. A suite can be entirely
green, and even fully covering, while failing to notice that the implementation is wrong.

## 1. Existing mutation capabilities found

The audit searched `skills/`, `agents/`, `tools/`, `templates/`, `archetypes/`, `adapters/`, `catalog/`,
`evals/`, and `.azuredevops/` for mutation testing, test quality, test robustness, test adequacy, PIT,
Stryker, mutmut, mutation score, surviving mutants, and TDD validation.

| Classification | Existing capability | Finding |
|---|---|---|
| OVERLAP | `tools/evals/run_mutations.py`, `evals/mutations/`, `tools/evals/check_methodology_contracts.py`, `.azuredevops/templates/mutation-validation.yml` | A complete mutation system already existed, but its subject is **canonical Commons methodology**, not application code. It mutates skills and contracts to prove the Commons evaluations detect degraded agent behavior. It shares the vocabulary and none of the inputs, gates, baselines, or owners. |
| PARTIAL | dashboard `test-quality` domain and `legacy-test-quality` information domain | A canonical location for test-quality reporting existed with tests, coverage, and assessment, but no mutation model, no drill-down dimensions, and no way to represent unsupported or unanalyzed mutation state. |
| PARTIAL | `design-test-strategy` | Selected risk-based test layers and explicitly refused coverage as behavioral proof, but had no notion of test strength or defect detection. |
| PARTIAL | `test-driven-development` | Owned RED, GREEN, and REFACTOR with recorded evidence, and treated a passing broader gate plus satisfied acceptance behavior as completion. |
| PARTIAL | `verify-openspec-implementation`, `audit-delivery-traceability` | Required a credible oracle per acceptance criterion and a `... -> test -> result -> verification` chain, but could not distinguish a criterion with a test from a criterion with a test that detects incorrect behavior. |
| PARTIAL | `test-behavior-reviewer` agent | Already challenged RED validity, mocks, boundaries, and coverage-only false confidence. |
| MISSING | application mutation testing | No capability mutated implemented application code to evaluate that project's test strength. |
| MISSING | language tooling | Zero references to PIT, Stryker, Stryker.NET, or mutmut existed anywhere in the repository. |
| MISSING | survivor classification, equivalent-mutant policy, mutation baselines, changed-code mutation scope | None existed in any form. |

## 2. Create or reuse decision

**Created** one canonical skill, `mutation-testing`, because no existing capability evaluated whether
application tests detect implementation defects. **Reconciled** rather than duplicated the existing
methodology mutation system: the boundary is now documented in both directions, in
`evals/mutations/README.md`, `.azuredevops/README.md`, the mutation-validation template, and the skill's own
report contract.

Two decisions avoided duplication:

- No second mutation runner, score model, or baseline was added for Commons methodology. The existing one is
  correct for its subject and was extended only to protect the new capability.
- No new agent was created. `test-behavior-reviewer` already provided independent, findings-only test review,
  so mutation survivor classifications, equivalent-mutant acceptances, and hardening evidence were added to
  its remit under the existing Skill-versus-Agent governance in `AGENTS.md`.

## 3. Skill and TDD responsibility boundary

| Workflow | Owns |
|---|---|
| `test-driven-development` | RED, GREEN, REFACTOR, and orchestration of the implementation and testing lifecycle |
| `mutation-testing` | whether the resulting tests detect meaningful implementation defects |

`test-driven-development` delegates to `mutation-testing` after GREEN and REFACTOR. It does not contain
mutation tooling, scope selection, survivor classification, or gate logic; the TDD skill grew by 25 lines and
its essence is unchanged. The delegation is one-directional and is enforced by a deterministic contract check
plus a Commons mutation that removes it.

Mutation testing never runs during the initial RED phase. The skill's own description and the TDD phase both
state this, and a scenario asserts it.

## 4. Supported technology strategy

The canonical skill is runtime and language neutral. Every ecosystem detail lives in
`references/tool-adapters.md`, and detection is deterministic via
`scripts/detect_mutation_tooling.py`, which enumerates ecosystems from real manifests, reports tooling the
project already configures, and reports unsupported source technologies rather than omitting them.

Selection rules: inspect the manifests that exist rather than inferring from file extensions; reuse existing
configuration as project convention; otherwise add the minimum configuration inside the existing build; never
introduce a parallel package manager or second build system; never install adapters speculatively.

## 5. Tool selection

| Ecosystem | Tool | Notes |
|---|---|---|
| JVM (Java; Kotlin and Scala with caveats) | PIT | Maven or Gradle plugin; JUnit 5 plugin where required; history-based incremental runs; source-control-scoped analysis. Kotlin and Scala produce materially more equivalent mutants. |
| .NET | Stryker.NET | Local dotnet tool pinned in the repository; diff-scoped runs against a baseline branch; its own break threshold is one input to the gate, not the gate. |
| JavaScript and TypeScript | StrykerJS | Runner package matched to the existing test framework; since-a-reference and incremental cache; type-only constructs yield low-value mutants. |
| Python | mutmut, or cosmic-ray for large parallel runs | Declared in the existing dependency group; diff scoping by computing changed paths. |
| Rust, PHP, Ruby | cargo-mutants, Infection, mutant | Same rules where the project uses them. |
| COBOL, PL/I, JCL, Natural, RPG, assembler, SQL dialects, configuration, generated bindings | none | `NOT_SUPPORTED` with a reason and the compensating verification. |

Exact command flags are deliberately not asserted as stable. The reference names the stable entry points and
instructs the agent to confirm option names against the version the project resolves, because these tools
change their command surfaces across major versions.

## 6. TDD integration

The default cycle is now RED, GREEN, REFACTOR, test-suite pass, mutation quality check, test hardening if
required, then validation against the specification. Three observable states replace an implicit single one:

```
TESTS_PASS -> MUTATION_CHECKED -> TEST_QUALITY_VALIDATED
```

A green suite establishes only the first. TDD completion now requires `TEST_QUALITY_VALIDATED` or an explicit
`NOT_SUPPORTED`, `BLOCKED`, or accepted-survivor result. `TEST_QUALITY_VALIDATED` was also added to the
project-memory checkpoint vocabulary rather than creating a parallel lifecycle.

## 7. OpenSpec integration

OpenSpec remains the behavioral authority. For every survivor the workflow asks whether an approved
requirement, specification, or acceptance criterion requires the mutated behavior:

- **yes** — the survivor most likely reveals a missing or weak test, classified `TEST_GAP`;
- **no** — it may be unspecified behavior, dead code, an equivalent mutation, a requirement gap, or behavior
  deliberately outside the specification, and a genuine requirement gap returns to the specification workflow.

The chain is specification, then expected behavior, then test, then mutation. It is never mutation score, then
arbitrary additional tests. `verify-openspec-implementation` consumes the recorded gate result as
test-quality evidence and remains the only workflow that can mark a specification PASS, PARTIAL, FAIL, or
BLOCKED; a critical surviving mutant against a criterion in scope prevents `PASS` for that criterion.

## 8. Survivor classification

A surviving mutant is a question, not a verdict. `references/survivor-classification.md` defines seven
categories with the evidence each requires: `TEST_GAP`, `EQUIVALENT_MUTANT`, `UNSPECIFIED_BEHAVIOR`,
`DEAD_CODE`, `LOW_VALUE_MUTATION`, `TESTABILITY_PROBLEM`, and `FLAKY_OR_INFRASTRUCTURE`. Nothing defaults to
`TEST_GAP`, and an unclassified survivor blocks the assessment rather than being averaged into a score.

The hardening loop requires naming the affected behavior, finding the linked requirement, **explaining why the
existing tests missed it**, adding one behavioral test, proving it fails against the mutant, proving it passes
against the correct implementation, and rerunning the scope. Reporting "the mutation score is low" is
explicitly insufficient.

Survivors must not be answered by distorting production code, and hardened tests must assert behavior,
contracts, outputs, side effects, and invariants — not private details, internal call sequencing, or arbitrary
constants. The reference maps each survivor signal to the right test: a `<` to `<=` survivor calls for a
boundary test, a removed guard for an invalid-input test, a changed operator for a worked business-rule
example.

## 9. Equivalent-mutant policy

One hundred percent mutation score is neither realistic nor desirable, and the documentation says so. An
equivalent, low-value, or justified dead-code survivor is excluded from the meaningful denominator **only when
it carries a recorded reason**. An unjustified equivalence claim stays in the denominator and raises a
warning, so a survivor cannot be dismissed by label alone. Agents are explicitly told not to modify correct
code or invent meaningless assertions to kill every mutant.

## 10. Quality gates

Statuses are `PASS`, `WARNING`, `FAIL`, `BLOCKED`, and `NOT_SUPPORTED`, derived by
`scripts/assess_mutation_quality.py` from the run, optional policy, and optional baseline. The gate is never
asserted in prose, and the run may not assert its own mutation score.

Hard failures: a critical behavioral mutant survives regardless of aggregate score; changed business logic has
meaningful survivors; the score materially regresses against the accepted baseline; a deliberately configured
minimum is missed; the normal suite failed before mutation; the tooling reported invalid execution.

Warnings: non-critical meaningful survivors; small deterioration within tolerance; plausible but unargued
equivalence; tooling unavailable for a low-risk module while critical scope was still assessed.

Blocked: an unstable baseline (`BLOCKED_BY_FLAKY_TESTS`), a crashed or unparseable run, an unresolvable scope,
or an unclassified survivor.

No arbitrary global threshold was introduced. There is no rule that a fixed percentage always passes.
Regression comparison against the last accepted baseline is the primary mechanism; an absolute minimum applies
only where a project deliberately configures one, optionally per criticality tier. Criticality tiers drive
strictness, so a financial calculation receives stronger scrutiny than a trivial getter, and generated code
and trivial boilerplate are excluded from scope by default with the exclusion recorded.

`NOT_SUPPORTED` exits non-zero (3) precisely so it cannot be mistaken for a pass; `--allow-not-supported`
lets a project accept it for a low-risk module while the status is still reported.

## 11. Changed-code strategy

Four scope profiles exist: `LOCAL`, `PR`, `NIGHTLY`, and `WEEKLY_DEEP`. Changed-code scoping resolves the diff
against the merge base, maps changed production files, classes, or methods, adds directly dependent impacted
code, and targets only that set with its relevant tests. Full mutation analysis is never forced after a small
edit, and a broader profile than the trigger justifies is prohibited. Where the tooling supports it —
PIT, Stryker.NET, and StrykerJS all do — diff scoping is the default for the implementation and pull-request
profiles.

## 12. Pull-request strategy

Normal tests, then targeted mutation on changed critical production code, then the gate. The
`fail_on_changed_business_logic_survivors` policy defaults to true, so a changed-code run that leaves
meaningful survivors in any business-logic tier fails: that is the point of a pull-request gate. Full-project
mutation on every pull request is discouraged unless run cost is genuinely negligible.

## 13. Nightly and weekly strategy

Nightly: normal tests, integration tests, a broader mutation suite over actively maintained or high-value
modules, baseline comparison, and a quality report. Weekly: optional full or deep analysis, expensive
operators, repeated survivor analysis, and historical trend. This separates fast feedback from deep quality
analysis.

These profiles are stated as methodology in `references/quality-gates.md`, not as provider-specific YAML.
Agent Commons does not currently generate CI templates for delivery projects, so no Azure template was added
for application mutation testing; `.azuredevops/README.md` now states that boundary explicitly, and the
existing methodology mutation template is annotated so the two systems cannot be confused.

## 14. Dashboard integration

`assets/dashboard-structure.json` gained a `test_quality_model` contract for the existing test-quality domain:
tests, coverage where available, mutation score, killed mutants, surviving meaningful mutants, critical
survivors, accepted equivalent mutants, mutation trend against the baseline, and one test-quality status.

Coverage is marked not required with an explicit note that it is never a substitute for mutation quality.
The five canonical global domain states were left unchanged; mutation-specific states live inside the
test-quality model as `GOOD`, `ADEQUATE`, `WEAK`, `NOT_YET_ANALYZED`, `NOT_SUPPORTED`, and
`BLOCKED_BY_FLAKY_TESTS`. Not-yet-run and unsupported states are shown rather than omitted.

Drill-down reaches module, changed-code scope, individual survivor, mutation operator, linked requirement and
specification, linked tests, and recommended action. Management Overview carries only aggregate status,
critical survivor count, and trend. The model explicitly prohibits presenting coverage as mutation quality,
omitting the mutation row, aggregating application results with Commons methodology results, and vanity
metrics.

`build_dashboard.py` projects the mutation summary deterministically into the existing domain reason, and
defaults to `NOT_YET_ANALYZED` when no mutation record exists.

## 15. Project-memory integration

Compact state only: last run date, scope, tool, score and status, meaningful and critical survivor counts,
accepted equivalent mutants, baseline and comparison verdict, and unresolved test gaps with their requirement
or specification IDs. Raw reports are referenced by path or artifact ID and never placed in hot memory.
`continue-project` now routes green implementation with unresolved meaningful survivors to test hardening
rather than reporting the implementation complete.

## 16. Evaluations

| Layer | Evidence |
|---|---|
| Skill scenarios | `evals/skills/scenarios.yaml` gained a `mutation-testing` entry with 10 scenarios: strong tests, weak-but-green suite, boundary survivor, equivalent mutant, critical business rule, unsupported technology, flaky baseline, changed-code scope, unspecified behavior, and baseline regression. |
| TDD scenarios | Two new scenarios assert the mutation hardening loop after REFACTOR and that mutation is not attempted during RED. New invariants and failure modes were added. |
| Contract and golden | `mutation-testing` was registered as a critical capability with a level-1 source contract, a level-1 deterministic unittest scenario, and a level-2 independently judged behavioral scenario, with golden expected facts, invariants, and four hard assertions. |
| Executable | `evals/tools/test_mutation_quality.py`, 27 tests, all passing: 5 benchmark, 19 gate, 3 tooling detection. |
| Dashboard | 5 new tests covering mutation metric projection, not-yet-analyzed, unsupported, flaky-blocked, and the canonical test-quality model. |
| Commons methodology mutation | 8 new cases in `evals/mutations/methodology-cases.json`. All 14 cases detected; mutation score 1.0. |

The eight self-protecting mutations demote a surviving critical mutant to a warning, let unsupported tooling
pass, remove the TDD mutation delegation, permit distorting production code to kill a mutant, disable the
critical-survivor gate branch, make an unsupported run exit zero, score a flaky baseline instead of blocking,
and strip the dashboard mutation-quality model. Each is detected, so the test-quality capability cannot
silently weaken — including the exact degradation named in the task: weakening "critical surviving mutant must
fail" to "critical survivor warning".

Two gate integrity properties are also tested: a run may not assert its own mutation score, and an unaccounted
survivor cannot silently improve the score.

## 17. Benchmark

`evals/fixtures/mutation-quality/` contains a synthetic invoice-totalling service with a reduced-rate
threshold and a validated discount, standing in for REQ-017 and SPEC-004. Two suites target identical
production code, and both are entirely green.

Measured, by real execution rather than assertion — each mutation is applied to a disposable copy and both
suites are run:

| | Weak suite | Hardened suite |
|---|---|---|
| Tests, all passing | 4 | 7 |
| Meaningful mutants | 4 | 4 |
| Killed | 1 | 4 |
| Meaningful survivors | 3 | 0 |
| Critical survivors | 3 | 0 |
| Mutation score | 25% | 100% |
| Accepted equivalent mutants | 1 | 1 |
| Gate | FAIL | PASS |

The first row combined with the last is the whole point: both suites are green, so a passing-test signal
cannot distinguish them, while mutation testing can. The weak suite never asserts the reduced-rate boundary,
the inclusive maximum discount rate, or the negative-rate rejection, so three financial-calculation defects
pass unnoticed. Each hardened test came from one classified survivor and asserts an acceptance criterion.
MUT-005 survives both suites and stays accepted, because killing it would require asserting the evaluation
order of two side-effect-free disjuncts, which no criterion requires.

## 18. Performance

Every run captures wall-clock runtime, total mutants, mutants per second where the tool reports it, affected
tests, timeout count, and excluded code, and those figures are used to tune scope. Supported optimizations are
the tooling's own: test impact analysis, incremental or since-a-reference analysis, result caches and history
files, changed-class selection, and parallel execution within the real core budget. Cache and history files
are build artifacts, not canonical state. Test quality is never traded away to shorten a run, and narrowing
the mutated set to make a gate pass is treated as a reporting defect.

Mutation operators start from each tool's default or proven set. Operators are never implemented by hand, and
stronger operators are evaluated only for critical domains where the added survivors prove meaningful.

## 19. Limitations

- **No mutation engine is installed or executed in this repository.** The benchmark provides genuine mutation
  evidence using the same disposable-copy technique as the existing Commons mutation runner, over five
  declared operators against a Python fixture. The `runs/` fixtures represent realistic PIT, Stryker, and
  mutmut output but were authored to the normalized contract rather than produced by those tools. No claim is
  made that PIT, Stryker.NET, StrykerJS, or mutmut was executed end to end here.
- **Adapter command flags are unverified against live tool versions.** The reference names stable entry points
  and instructs the agent to confirm exact options against the resolved version. This is deliberate: asserting
  flags that drift across major versions would be worse than requiring confirmation.
- **The benchmark is Python and single-module.** Multi-module JVM reactors, .NET solutions, and monorepo
  scope resolution are described in the adapters reference but not exercised by an executable test.
- **Criticality classification is a judgement.** The gate derives its status deterministically from a declared
  tier, but nothing verifies that the declared tier is correct for the code. An independent
  `test-behavior-reviewer` pass is the intended control.
- **The level-2 behavioral scenario requires the semantic runtime** and was not executed as part of this
  change; only the deterministic level-1 layers were run locally.
- **Equivalent-mutant detection remains manual.** No automated equivalence checking exists; the policy
  requires a recorded argument, and an unargued claim is penalized rather than trusted.
- **No mutation baseline is seeded for any project.** The baseline contract and comparison logic exist, but a
  project must accept its own first baseline from a passing run.
