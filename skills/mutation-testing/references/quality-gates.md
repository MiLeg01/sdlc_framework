# Mutation quality gates, scope profiles, and baselines

## Criticality tiers

Not all code deserves identical treatment. Classify the mutated scope and apply the matching expectation.

| Tier | Examples | Expectation |
| --- | --- | --- |
| `SECURITY_CRITICAL` | authorization, tenancy isolation, secret handling, input trust boundaries | no meaningful survivor may be accepted without an explicit recorded risk decision |
| `FINANCIAL_OR_CALCULATION` | pricing, tax, interest, rounding, reconciliation, quantity maths | no meaningful survivor may be accepted without an explicit recorded risk decision |
| `CRITICAL_BUSINESS_LOGIC` | eligibility, state machines, regulatory rules, decision routing | no meaningful survivor may be accepted without an explicit recorded risk decision |
| `INTEGRATION_CONTRACT` | schema and protocol semantics, provider and consumer expectations, message contracts | meaningful survivors are hardened by default; acceptance requires a reason |
| `NORMAL_BUSINESS_LOGIC` | ordinary transformations, orchestration, local rules | meaningful survivors are hardened where cost is proportionate; acceptance requires a reason |
| `PLUMBING_OR_TRIVIAL` | wiring, accessors, data-transfer objects, logging | survivors are usually `LOW_VALUE_MUTATION`; excluded from scope by default |
| `GENERATED_CODE` | source-generator, framework binding, and compiler output | excluded from scope by default |

A survivor is **critical** when it is classified `TEST_GAP` or `UNSPECIFIED_BEHAVIOR` and its code sits in the
first three tiers. A financial calculation deserves stronger scrutiny than a trivial getter, and the gate
reflects that rather than averaging them together.

## Scope profiles

| Profile | Scope | Typical trigger |
| --- | --- | --- |
| `LOCAL` | changed production code, its module, and the code linked to the current specification, with the directly relevant tests | inside the implementation and TDD loop |
| `PR` | changed production code plus critical impacted code | pull-request validation |
| `NIGHTLY` | actively maintained or high-value production modules | scheduled build |
| `WEEKLY_DEEP` | full analysis, expensive operators, repeated survivor and trend analysis | scheduled deep build |

Changed-code scoping resolves the diff against the merge base, maps changed production files, classes, or
methods, adds the directly dependent impacted code, and targets only that set. Do not run full-project
mutation analysis after every small edit, and do not use a broader profile than the trigger justifies.

## Statuses

| Status | Meaning |
| --- | --- |
| `PASS` | the run executed validly, no critical survivor remains, and no material regression against the accepted baseline |
| `WARNING` | the run is valid and non-blocking issues remain |
| `FAIL` | a hard failure condition below is met |
| `BLOCKED` | the run could not produce trustworthy results |
| `NOT_SUPPORTED` | no maintained mutation tooling applies to the technology in scope |

### Hard failures

- a critical behavioral mutant survives, regardless of the aggregate score;
- changed business logic in scope has surviving meaningful mutants;
- the mutation score materially regresses against the accepted baseline;
- a deliberately configured absolute minimum score is not met;
- the normal test suite fails before mutation execution;
- the mutation tooling reports invalid execution.

### Warnings

- non-critical meaningful survivors remain;
- the score deteriorated slightly, within the configured regression tolerance;
- survivors are plausibly equivalent but not yet argued and accepted;
- mutation tooling is unavailable for a low-risk module while the critical scope was still assessed.

### Blocked

- the baseline suite is flaky, order-dependent, or environment-dependent; report
  `BLOCKED_BY_FLAKY_TESTS` as the reason;
- the tool crashed, timed out globally, or produced an unparseable report;
- the mutated scope could not be resolved.

An unsupported technology is never a pass. Report `NOT_SUPPORTED` with the reason and the compensating
verification actually performed.

## Score policy

There is no universal threshold. Do not adopt a rule such as "eighty percent always passes". Acceptable
mutation quality depends on technology, module, criticality, existing baseline, equivalent-mutant density, and
test architecture, and one hundred percent is neither realistic nor desirable.

Two mechanisms are supported and both may be active:

1. **Absolute minimum** — used only where a project deliberately configures one, per module or tier.
2. **Regression comparison** — the primary mechanism. Compare the current run against the last accepted
   baseline for the same scope, and fail on a material drop.

The score is computed over meaningful mutants: killed meaningful mutants divided by total meaningful mutants,
where accepted equivalent and low-value mutants are excluded from both terms and reported separately. A score
alone is never the gate.

## Baseline

Store the last accepted mutation result per scope: tool and version, scope definition, total and meaningful
mutant counts, killed and survived counts, score, critical survivor count, accepted equivalent mutants, and
the commit the baseline was accepted at.

Compare and report both sides, for example:

```
                       BASELINE    CURRENT
Mutation score            87.5%      89.2%
Critical survivors            0          0
Test gaps                     8          5
Overall: IMPROVED
```

Never promote a baseline from a `FAIL`, `BLOCKED`, or `NOT_SUPPORTED` run. Promote only from a `PASS`, and
record the promoting commit. A baseline whose scope definition changed is a new baseline, not an update; a
score comparison across different scopes is not a regression signal.

## Continuous integration profiles

These are recommendations for whichever CI system the project already uses. Keep the canonical methodology
independent of any specific provider, and keep provider-specific YAML in the project.

| Stage | Sequence |
| --- | --- |
| Pull request | normal tests, then targeted mutation on changed critical production code, then the gate |
| Main | normal tests, then broader targeted mutation where run cost permits, then the gate |
| Nightly | normal tests, integration tests, broader mutation suite, baseline comparison, quality report |
| Weekly | optional full or deep mutation, expensive operators, repeated survivor analysis, historical trend |

Avoid full-project mutation on every pull request unless the project is small enough that the run cost is
genuinely negligible. Application mutation testing is an application test system; do not couple it to an
agent-methodology evaluation system.

## Runtime optimization

Use the tooling's own optimizations rather than reducing rigor: test impact analysis so only covering tests run
against each mutant, incremental or since-a-reference analysis, a result cache or history file, changed-class
selection, and parallel execution within the real core budget. Cache and history files are build artifacts and
are not canonical state.

Capture cost on every run: wall-clock runtime, total mutants, mutants per second where the tool reports it,
number of affected tests, timeout count, and excluded code. Use those numbers to tune scope. Do not sacrifice
test quality to shorten a run, and do not narrow the mutated set purely to make a gate pass.

## Mutation operators

Start from the tool's default or proven operator set. Do not indiscriminately enable every available operator,
and do not implement operators by hand when mature language tooling already provides them. For critical
domains, evaluate stronger operators only where the added survivors prove to be meaningful. Common categories
include conditional boundaries, boolean replacement, arithmetic replacement, return-value changes, null
behavior, branch removal, and method-call removal.
