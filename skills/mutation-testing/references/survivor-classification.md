# Surviving-mutant classification and the test-hardening loop

A surviving mutant is a question, not a verdict. Classify it before deciding what to do, and never label every
survivor a test gap by default. Misclassification in either direction is costly: calling an equivalent mutant a
test gap produces meaningless assertions, and calling a real test gap an equivalent mutant hides a defect the
suite cannot catch.

## Categories

| Classification | Meaning | Required evidence | Action |
| --- | --- | --- | --- |
| `TEST_GAP` | A test should detect this mutation and does not | the specification or acceptance criterion that requires the mutated behavior, plus the tests that execute the code but do not assert it | harden the test |
| `EQUIVALENT_MUTANT` | The mutation does not semantically change program behavior | the argument for behavioral equivalence, such as an unreachable branch outcome, an idempotent operation, or a value that cannot differ for any admissible input | accept with recorded reason |
| `UNSPECIFIED_BEHAVIOR` | The code has behavior, but no specification defines what it should be | the search performed for a governing requirement or criterion, and the result | route to the specification workflow; do not invent a test |
| `DEAD_CODE` | The mutated behavior cannot be reached | the reachability argument or the absent caller | remove the code, or record why it must remain |
| `LOW_VALUE_MUTATION` | The mutation affects trivial or non-semantic behavior | the reason the behavior carries no contract, such as logging text or a type-only construct | accept with recorded reason |
| `TESTABILITY_PROBLEM` | Architecture makes the behavior impractical to test properly | the specific coupling, hidden state, or missing seam that blocks a behavioral assertion | record as a design finding with the residual risk |
| `FLAKY_OR_INFRASTRUCTURE` | The result is unreliable because of the environment | the evidence of instability, such as an inconsistent repeat, a timeout, or a resource failure | stabilize first; the run is not trustworthy |

`TEST_GAP` and `UNSPECIFIED_BEHAVIOR` are the two meaningful survivor outcomes for a quality gate.
`EQUIVALENT_MUTANT` and `LOW_VALUE_MUTATION` are excluded from the meaningful denominator once accepted with a
reason. `FLAKY_OR_INFRASTRUCTURE` invalidates the run rather than contributing to a score.

## Deciding between a test gap and unspecified behavior

Ask whether an approved requirement, OpenSpec specification, or acceptance criterion requires the mutated
behavior.

- **Yes** — the survivor reveals a missing or weak test. Classify `TEST_GAP` and harden.
- **No** — the survivor may be unspecified behavior, dead code, an equivalent mutation, a requirement gap, or
  implementation behavior deliberately outside the specification. Classify accordingly. When it is a genuine
  requirement gap, return it to the specification workflow.

The correct chain is specification, then expected behavior, then test, then mutation. It is never mutation
score, then arbitrary additional tests. Do not create tests solely to raise a number.

## The test-hardening loop

Run this loop once per meaningful survivor:

1. **Identify the affected behavior.** Name what the mutated code is supposed to do, in terms a stakeholder
   would recognize, not in terms of the mutated token.
2. **Find the linked requirement or specification.** Record the requirement and specification IDs and the
   acceptance criterion. If none exists, stop and reclassify.
3. **Determine why the existing tests missed it.** State the actual cause: the case is never exercised, the
   input never reaches the boundary, the assertion checks a weaker property than the contract, the outcome is
   asserted only through a mock, or the error path is unasserted. This explanation is the deliverable. Do not
   report "the mutation score is low" and stop.
4. **Create or improve one behavioral test.** Assert behavior, contract, output, side effect, or invariant.
5. **Prove the test fails against the mutant.** Apply the mutation in a disposable copy, observe the new test
   failing for the intended reason, and record it. A hardening claim without this evidence is unproven.
6. **Prove the test passes against the correct implementation.** Restore the unmutated code and record the
   test passing.
7. **Rerun the relevant mutation scope.** Confirm the mutant is now killed and that no previously killed
   mutant regressed.

Never modify correct production behavior to kill a mutant. If a mutant can only be killed by changing code
that is already correct, the mutant is equivalent, low value, or the specification is wrong; it is not a
license to distort the implementation.

## Test-design targets

When a survivor reveals weak coverage, prefer tests that target boundaries, negative paths, error handling,
business rules, state transitions, and integration contracts:

| Survivor signal | Test to add |
| --- | --- |
| a comparison boundary changed, such as `<` to `<=` | a boundary test at the exact threshold and at one value on each side |
| a validation or guard was removed | an invalid-input test asserting the rejection and its observable effect |
| an arithmetic or calculation operator changed | a worked business-rule example with an independently derived expected value |
| a return value was replaced with a constant or default | a test asserting the real computed contract, not merely a non-null result |
| a conditional branch was removed | a test for the alternative path's observable outcome |
| a method call was removed | a test asserting the side effect or downstream contract that call exists to produce |

## Tests that must not be written

Killing a mutant with a bad test is worse than leaving it alive, because it adds maintenance cost and false
confidence at once. Do not assert private implementation details, exact internal method sequencing, call counts
that no contract requires, or arbitrary constants unrelated to the specification. Do not add a snapshot whose
expected value was copied from current output without checking it against the specification. Do not weaken an
existing assertion to make an unrelated test pass.

Mutation testing exists to strengthen behavioral confidence. An over-coupled suite that scores well is a worse
outcome than a behavioral suite with a documented, accepted survivor.
