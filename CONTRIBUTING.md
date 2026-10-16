# Contributing to Agent Commons

Agent Commons accepts reusable engineering capabilities that are generic, bounded, testable, and safe to
share. Canonical methodology is runtime-neutral; runtime-specific discovery and rendering belong in
adapters or installation logic.

## Capability boundaries

Choose the smallest correct abstraction:

- **Skill:** a bounded workflow with clear use and non-use guidance.
- **Agent:** an independently delegated responsibility where isolated context or perspective adds value.
- **Tool:** deterministic behavior with stable inputs, outputs, and failure modes.
- **Template:** reusable structure without embedded unverified judgment.
- **Archetype:** a project-family composition profile referencing stable capability IDs.
- **Overlay:** a cross-cutting composition concern used by more than one project family.
- **Adapter:** a thin mapping from canonical capability into a runtime's real feature model.
- **Eval:** behavioral or deterministic evidence protecting a meaningful contract.

Do not add an agent that merely restates a skill. Do not add a skill that combines unrelated
responsibilities. Prefer merging or extending a canonical capability over retaining semantic duplicates.

## What belongs in Commons

A contribution should be:

- useful beyond one project;
- independent of client identities, private repositories, and workstation paths;
- explicit about trigger, non-trigger, scope, outputs, validation, and failure handling;
- compatible with the runtime-neutral canonical model;
- supported by scenarios or deterministic tests;
- worth its long-term discovery and maintenance cost.

Keep project-specific business rules, package structures, deployment assumptions, screenshots, internal
URLs, source excerpts, credentials, and temporary workarounds in the project that owns them.

Use synthetic examples and parameterized paths. Generated data must be reproducible from canonical input.

## Runtime-neutral core

Canonical capability bodies live once under `skills/`, `agents/`, `tools/`, or `templates/`.

Runtime-specific paths, syntax, precedence, installation destinations, feature limitations, and wrapper
formats live under `adapters/` or `install/`. Never maintain separate canonical workflow copies for Codex,
Claude Code, Cline, and OpenCode.

When adding runtime support, verify official current behavior and document unsupported concepts honestly.
Add tests for discovery, rendering, coexistence, idempotency, drift, repair, removal, and user-content
preservation as applicable.

## Project-to-Commons governance

Use `review-for-commons` inside the source project to create a sanitized proposal. The review is
proposal-only and must not mutate this repository.

After the user selects exact candidates, use `promote-to-commons` to revalidate:

- semantic overlap and naming collisions;
- abstraction type and bounded scope;
- maturity and reuse evidence;
- confidentiality and private-path removal;
- licensing and required attribution;
- runtime neutrality and adapter impact;
- evaluation and validation feasibility.

Promotion may still conclude that the behavior is duplicate, project-local, unsafe, or insufficiently
proven. Approval authorizes evaluation of the selected candidate; it does not guarantee inclusion.

## External capability governance

External discovery never installs or activates a capability. Review one revision-pinned item at a time and
separate source facts from Agent Commons interpretation.

Record the applicable relationship:

- `COPIED`
- `ADAPTED`
- `INSPIRED-BY`
- `INDEPENDENT-REIMPLEMENTATION`

Unknown licensing prohibits copying and adaptation. Preserve legally required copyright, license, notice,
and attribution text in a current product-appropriate location. Do not rely on temporary discovery output
for legal compliance.

Executable third-party content requires explicit security review covering scripts, hooks, remote tooling,
credentials, network access, filesystem access, Git mutation, dependency installation, privilege, and
untrusted instructions. Do not execute retrieved content merely to inspect it.

## Required updates

When behavior changes, update the smallest complete set of canonical artifacts:

1. capability source;
2. catalog metadata and relationships;
3. affected archetype or overlay composition;
4. runtime adapter behavior or documented limitations;
5. behavioral scenarios and executable tests;
6. generated capability index and presentation facts;
7. current product documentation;
8. `VERSION` and `CHANGELOG.md` when release semantics change.

Do not add development-history reports, benchmark captures, browser traces, caches, downloaded packages,
or private provenance to the product tree.

## Validation

Run focused tests during implementation and the full gate with Python 3.11 or newer before committing:

```bash
python3 tools/evals/run_evals.py --changed --base origin/main
python3 tools/runtime_adapters.py validate
python3 tools/resolve_archetypes.py validate
python3 tools/resolve_capability_gaps.py validate
python3 tools/external_capabilities.py validate
python3 tools/refresh_commons_presentation.py --check
python3 tools/validate_commons.py
```

The command above is the local deterministic gate and reports unavailable external semantic scenarios as
warnings. Required CI must provide independent executor and judge commands, add `--require-semantic`, and use
stochastic repeats appropriate to the PR, nightly, or weekly profile.

Then run the complete unittest command documented in [`README.md`](README.md#validation).

Behavior changes should demonstrate a behavior-relevant failing test before implementation, the identical
test passing afterward, and the broader repository gate. Visual changes additionally require static HTML
validation and real-browser QA at representative desktop, laptop, tablet, and mobile widths.

Installer changes must cover safe ownership, idempotency, status, doctor, verify, repair, managed removal,
platform path abstraction, and preservation of unrelated user content.

## Confidentiality and release hygiene

Before committing:

- inspect the full diff and preserve unrelated work;
- search for private paths, personal names, project identities, client terms, internal URLs, credentials,
  raw logs, and proprietary source excerpts;
- verify every local documentation link and every catalog path;
- refresh generated data instead of hand-editing it;
- remove caches, build output, screenshots, traces, and temporary exports;
- confirm third-party notice obligations are current;
- run the complete validation gate.

## Versioning

Use semantic versioning. `VERSION` contains the canonical numeric value. Human-facing release labels use a
leading `v`.

- Patch: compatible fixes or documentation corrections.
- Minor: backward-compatible capability additions or meaningful extensions.
- Major: incompatible public contract changes.

Release notes describe the current product surface, not internal development chronology.
