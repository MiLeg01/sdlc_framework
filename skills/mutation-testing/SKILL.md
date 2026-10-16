---
name: mutation-testing
description: Evaluate whether an existing test suite would actually detect defective implementation behavior by running targeted mutation analysis, classifying surviving mutants against approved specifications, and strengthening tests through a behavioral hardening loop. Use after implementation reaches a stable green and refactored state, when auditing an inherited or legacy-characterization suite, or as a changed-code quality gate. Do not use during the initial RED phase, as a substitute for test-driven development or coverage, to justify changing correct production behavior so a mutant dies, or to raise a score with implementation-coupled assertions.
---

# Assess and harden test quality with mutation testing

Passing tests are not evidence of strong tests. A suite can be entirely green, and even fully covering, while
still failing to notice that the implementation is wrong. Mutation testing introduces controlled changes to
production code and asks one question: **would the test suite notice?**

Keep the three questions distinct and never substitute one for another:

| Practice | Question it answers |
| --- | --- |
| Code coverage | Was this code executed by tests? |
| Test-driven development | Did we specify the behavior through tests before implementing it? |
| Mutation testing | Would those tests fail if the implementation were wrong? |

Full coverage does not imply test quality, and a green suite does not imply defect detection. This workflow
owns test-strength evaluation only. `test-driven-development` owns RED, GREEN, and REFACTOR and delegates
here once meaningful implementation exists. Do not run mutation analysis during the initial RED phase, and do
not reimplement the red-green-refactor loop inside this workflow.

## Terminology

- **Mutant** — one controlled modification to production code, such as `a > b` becoming `a >= b`,
  `return true` becoming `return false`, or `+ 1` becoming `- 1`.
- **Killed mutant** — at least one test fails after the mutation, so the suite detected the injected defect.
- **Surviving mutant** — every test still passes despite the mutation, which indicates a possible
  test-quality gap but is not yet proof of one.
- **Equivalent mutant** — the mutation does not semantically change program behavior, so survival is not a
  test defect and must not be reported as one.
- **Mutation score** — killed meaningful mutants divided by total meaningful mutants. It is one signal among
  several and never the sole quality gate.

## Establish preconditions

1. Confirm the implementation is stable: focused tests are green, the refactor step is complete, and the
   change is not mid-edit.
2. Run the project's normal required test gate and record the exact command and result. Mutation results are
   meaningless if the baseline does not pass.
3. Judge baseline stability. If the suite is flaky, order-dependent, clock-dependent, or environment-dependent,
   stop and report `BLOCKED_BY_FLAKY_TESTS`. Random failures must never be counted as killed mutants.
4. Resolve the behavioral authority. When OpenSpec governs the change, retain the specification, requirement,
   and acceptance-criterion IDs in scope. OpenSpec remains the authority on what behavior must exist.
5. Read local governance for tooling policy. Some repositories prohibit adding a build dependency; that
   constraint outranks this workflow.

## Select scope

Full mutation analysis is expensive. Match scope to the lifecycle stage instead of mutating everything after
every edit.

| Profile | Target | Goal |
| --- | --- | --- |
| Local implementation loop | changed production code, its module, and the code linked to the current specification | fast feedback inside the TDD loop |
| Pull-request gate | changed production code plus critical impacted code | prove the change did not introduce weakly tested behavior |
| Nightly | actively maintained or high-value production modules | broader regression signal against the accepted baseline |
| Weekly deep | full or expensive analysis where system size permits | trend, expensive operators, repeated survivor analysis |

Prefer changed-code analysis in the implementation and pull-request profiles wherever the tool supports it:
resolve the diff against the merge base, map changed production classes, methods, or files, add the directly
dependent impacted code, and target only that set with its relevant tests.

Weight scope by criticality rather than treating all code identically. Apply the strictest expectations to
security-critical, financial or calculation, and critical business-rule behavior, then integration contracts,
then normal business logic. Exclude generated code, framework-generated bindings, trivial accessors, and
non-executable declarations unless a specific risk justifies the compute. `references/quality-gates.md`
defines the criticality tiers, scope profiles, and baseline comparison model.

## Select tooling

The canonical workflow is runtime and language neutral. Detect the project's actual build and test system
first, then choose one adapter. Run `scripts/detect_mutation_tooling.py --root <project>` to enumerate
detected ecosystems, the already-configured mutation tooling, and the recommended adapter or explicit
non-support. Reuse tooling the project already configures. Add only the minimum configuration required, keep
it inside the existing build system, and never introduce a parallel package manager or second build tool.

`references/tool-adapters.md` records the per-ecosystem integration, invocation, scope flags, changed-code
support, normalization notes, and known limits for the JVM, .NET, JavaScript and TypeScript, and Python
ecosystems, plus the rule for everything else. When no maintained tool applies to a technology, report
`NOT_SUPPORTED` with the reason and the compensating verification. Never report an unsupported ecosystem as a
pass, and never install every adapter speculatively.

## Run, classify, and harden

1. Execute the selected tool over the selected scope and capture its native report plus runtime, mutant
   totals, timeouts, and exclusions.
2. Normalize the native report into the structured contract in `references/mutation-report-contract.md`.
   A run whose tooling reports invalid execution is `BLOCKED`, not a pass.
3. Classify every surviving mutant before deciding anything. `references/survivor-classification.md` defines
   the categories `TEST_GAP`, `EQUIVALENT_MUTANT`, `UNSPECIFIED_BEHAVIOR`, `DEAD_CODE`, `LOW_VALUE_MUTATION`,
   `TESTABILITY_PROBLEM`, and `FLAKY_OR_INFRASTRUCTURE`, with the evidence each one requires. Do not label
   every survivor a test gap by default.
4. For each survivor, ask whether an approved specification or acceptance criterion requires the mutated
   behavior. If it does, the survivor most likely reveals a missing or weak test. If it does not, the survivor
   may be unspecified behavior, dead code, an equivalent mutation, or a requirement gap; route a genuine
   requirement gap back to the specification workflow rather than inventing a test.
5. Harden tests for each meaningful survivor through the loop in `references/survivor-classification.md`:
   identify the affected behavior, find the linked requirement or specification, determine why the existing
   tests missed it, add or improve one behavioral test, prove that the test fails against the mutant, prove
   that it passes against the correct implementation, then rerun the relevant mutation scope.
6. Rerun the normal test gate after hardening, then rerun the targeted mutation scope. Report the before and
   after state.

Never modify correct production behavior to kill a mutant. Strengthen the test against expected behavior
instead. A survivor that can only be killed by changing correct code is not a test gap.

Generated and improved tests must assert behavior, contracts, outputs, side effects, and invariants. They must
not assert private implementation details, exact internal call sequencing, or arbitrary constants unrelated to
the specification. Prefer boundaries, negative paths, error handling, business rules, state transitions, and
integration contracts: a `<` to `<=` survivor calls for a boundary test, a removed-validation survivor calls
for an invalid-input test, and a changed-operator survivor calls for a worked business-rule example. The
objective is behavioral confidence, not a higher number.

## Apply the quality gate

Run `scripts/assess_mutation_quality.py --run <normalized-run.json>` with the optional project baseline and
criticality policy to derive the gate deterministically. Statuses are `PASS`, `WARNING`, `FAIL`, `BLOCKED`,
and `NOT_SUPPORTED`.

Do not impose one arbitrary global score. There is no universal rule that a fixed percentage always means
pass, because acceptable mutation quality depends on technology, module, criticality, existing baseline,
equivalent mutants, and test architecture. Support a deliberately configured absolute minimum where a project
sets one, and always support regression comparison against the last accepted baseline. A high aggregate score
does not excuse a surviving critical behavioral mutant. `references/quality-gates.md` defines the exact hard
failures, warnings, blocked conditions, and baseline promotion rule.

One hundred percent mutation score is neither realistic nor desirable. Equivalent mutants exist. A justified
equivalent or excluded mutant may be accepted with recorded evidence and a reason; it may not be hidden.

## Report and trace

Produce the structured run, metrics, and survivor records defined in
`references/mutation-report-contract.md`, then a short human-readable summary. Report the scope, tool,
baseline result, mutant totals, killed, survived, meaningful survivors, critical survivors, score, gate
status, the reason for that status, linked requirement and specification IDs, and the recommended action.
Never output a bare score, and never fabricate a metric the tool did not produce.

Extend the existing evidence chain rather than creating a parallel one:

```
SOURCE -> REQUIREMENT -> OPEN SPEC -> ACCEPTANCE CRITERION -> TEST -> MUTATION -> KILLED or SURVIVED
```

That chain is what turns "an acceptance criterion has a test" into "an acceptance criterion has a test that
actually detects incorrect behavior". Record capture cost as well: runtime, total mutants, mutants per second
where the tool reports it, affected tests, timeouts, and excluded code. Use those numbers to tune scope, and
never trade away test quality purely to shorten a run.

When project memory is enabled, merge only the compact state: last run, scope, tool, score, meaningful and
critical survivors, accepted equivalent mutants, baseline, and unresolved test gaps. Reference the raw report
by path or artifact ID; never store it in hot memory.

## Integration and direct use

`test-driven-development` delegates here after GREEN and REFACTOR, and `implement-ready-slice` invokes this
workflow for the changed scope before final validation, so a normal implementation does not require the user
to request mutation testing manually. `verify-openspec-implementation` consumes the gate result as test-quality
evidence and remains the only workflow that can mark a specification PASS, PARTIAL, FAIL, or BLOCKED. Ask a
fresh `test-behavior-reviewer` to challenge consequential survivor classifications, equivalent-mutant
acceptances, and hardening evidence; this workflow does not certify its own conclusions.

Invoke this skill directly by name, optionally with a specification, requirement, module, or path subject, to
audit an existing suite, review a targeted area, or assess inherited code. Direct use follows the same
preconditions, classification, and gate rules as the delegated path.

For legacy modernization, mutation testing assesses whether characterization tests meaningfully constrain the
behavior they claim to pin down, which is valuable before replacing or refactoring complex business logic.
Apply it to the migrated target implementation, the characterization harness, or an equivalent supported
implementation. Do not attempt to mutate an unsupported legacy source language merely because the capability
exists; report `NOT_SUPPORTED` for that source and state which supported artifact was assessed instead.

## Completion

Complete only when the baseline gate passed and was stable, the scope and tool are explicit, every survivor
carries a classification with evidence, meaningful survivors were either hardened against expected behavior
or explicitly accepted with a reason, the gate status is derived rather than asserted, and traceability links
resolve. Report `NOT_SUPPORTED`, `BLOCKED`, or partial results honestly instead of presenting an incomplete or
unsupported run as validated test quality.
