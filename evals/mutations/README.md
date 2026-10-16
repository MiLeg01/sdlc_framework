# Mutation checks

**Scope.** Everything in this directory is *Agent Commons methodology* mutation testing: it mutates canonical
skills, contracts, and helper logic to verify that the Commons evaluations detect degraded agent behavior. It
is repository quality infrastructure.

It is not the same system as *application* mutation testing, which is the `mutation-testing` skill: that
mutates an implemented project's application code to evaluate the strength of that project's tests. The two
share vocabulary — mutant, killed, survived, mutation score, critical survivor — and nothing else. They have
separate inputs, gates, baselines, and owners, and their results must never be aggregated into one score.
Application mutation testing must not depend on this semantic-evaluation infrastructure, and this
infrastructure must not consume application mutation reports.

The canonical mutation-testing capability is itself protected here: `methodology-cases.json` includes
mutations that demote a surviving critical mutant to a warning, let unsupported tooling pass, remove the TDD
mutation delegation, permit distorting production code to kill a mutant, disable the critical-survivor gate,
make an unsupported run exit zero, score a flaky baseline instead of blocking, and strip the dashboard
mutation-quality model. Each must be detected, so the test-quality capability cannot silently weaken.

Mutation cases prove that hard gates actually fail. Initial protected mutations cover source modification,
fabricated or missing evidence, invalid structured output, missing dashboard domains, absent TDD RED evidence,
requirements without required evidence, ownership escape, unaccounted relevant source, and canonical contract
drift. Add a mutation when a new hard assertion is introduced.

`methodology-cases.json` defines executable temporary mutations for full-scope legacy analysis, evidence-backed
requirements, RED-first TDD, dashboard test quality, dashboard ownership, and project-memory reuse. The runner
copies the repository to a temporary directory, applies one mutation, runs the specific behavioral or contract
test named by that case, and counts detection only when the expected failure is observed. It then deletes the
copy. Mutated production capability state is never
written to the canonical checkout.
