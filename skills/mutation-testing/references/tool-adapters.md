# Mutation tooling adapters

The canonical workflow is language neutral. This reference maps a detected ecosystem to one maintained tool,
its integration point in the project's existing build system, and its real limits. Detect first, then pick one
adapter. Never install every adapter, and never add a second build system or package manager to make a
mutation tool fit.

Command flags change between major tool versions. Treat the entry points below as stable and confirm exact
option names against the version the project actually resolves before relying on them in a gate.

## Selection rules

1. Inspect the build and test manifests that exist, not the language you assume from file extensions.
2. If mutation tooling is already configured, reuse it. An existing configuration is project convention and
   outranks the default in this table.
3. Otherwise select the adapter for the detected ecosystem and add the minimum configuration: the plugin or
   tool declaration, the mutated scope, the test scope, and the report format.
4. If no maintained tool covers the technology, report `NOT_SUPPORTED` with the reason and the compensating
   verification. Do not silently pass.
5. Record the resolved tool and version in the run report. A gate derived from an unrecorded tool version is
   not reproducible.

## Supported ecosystems

| Ecosystem | Detect | Tool | Integration |
| --- | --- | --- | --- |
| JVM (Java, and Kotlin or Scala with caveats) | `pom.xml`, `build.gradle`, `build.gradle.kts` | PIT (pitest) | Maven `pitest-maven` plugin or the Gradle pitest plugin, inside the existing build |
| .NET (C#, F#, VB.NET) | `*.sln`, `*.csproj`, `*.fsproj` | Stryker.NET | `dotnet-stryker` as a local dotnet tool with `stryker-config.json` |
| JavaScript and TypeScript | `package.json` | StrykerJS | `@stryker-mutator/core` plus the runner matching the project's test framework |
| Python | `pyproject.toml`, `setup.cfg`, `tox.ini` | mutmut, or cosmic-ray for large parallel runs | declared in the existing dependency group, not a new environment manager |

### JVM — PIT

PIT is the established JVM mutation engine and integrates as a build plugin rather than a separate runner.
Bind it to the existing Maven or Gradle build; add the JUnit 5 plugin when the project uses the JUnit 5
platform, because PIT's default provider targets JUnit 4. Restrict the mutated and tested sets explicitly by
class or package glob instead of mutating the whole reactor.

- **Scope** — target-class and target-test globs, resolved per module in a multi-module build.
- **Changed code** — PIT supports source-control-scoped analysis and incremental history, so the diff-scoped
  pull-request profile is achievable. Confirm which mechanism the project's PIT distribution provides before
  depending on it.
- **Optimization** — history files enable incremental runs, and PIT selects only the tests that cover each
  mutated line. Enable parallel threads within the agent's real core budget.
- **Caveats** — Kotlin and Scala compile to bytecode PIT can mutate, but both generate a materially higher
  share of equivalent mutants from null checks, synthetic bridges, and desugared constructs. Expect to
  classify more survivors as `EQUIVALENT_MUTANT` and do not chase a Java-equivalent score.
- **Report** — XML, HTML, and CSV output under the build's report directory; normalize the XML.

### .NET — Stryker.NET

Install `dotnet-stryker` as a local dotnet tool so the version is pinned in the repository manifest, and drive
it from the existing solution. Do not add a separate build system.

- **Scope** — file and member globs in `stryker-config.json`, plus explicit project and test-project
  selection in a multi-project solution.
- **Changed code** — Stryker.NET supports diff-scoped runs against a baseline branch, which is the correct
  default for the pull-request profile.
- **Optimization** — coverage-driven test filtering per mutant, and configurable concurrency.
- **Caveats** — the tool's own threshold model has a break value that fails the run. Treat that as one input
  to the canonical gate, not as the gate. Source generators and generated partials should be excluded.
- **Report** — JSON and HTML; normalize the JSON.

### JavaScript and TypeScript — StrykerJS

Add `@stryker-mutator/core` plus the runner package that matches the project's existing test framework, and
keep configuration in the framework's conventional config file. Reuse the project's test command; do not
introduce a second test runner.

- **Scope** — `mutate` globs, narrowed to changed files for the fast profiles.
- **Changed code** — StrykerJS supports since-a-reference diff scoping and an incremental mode backed by a
  cache file. The incremental cache is a build artifact and must not be committed as canonical state.
- **Optimization** — per-test coverage analysis, concurrency, and the incremental cache.
- **Caveats** — TypeScript type-only constructs produce mutants that cannot change runtime behavior; expect
  `LOW_VALUE_MUTATION` and `EQUIVALENT_MUTANT` classifications. Long-running end-to-end suites are a poor
  mutation target; scope mutation to unit and component layers.
- **Report** — JSON report plus the HTML dashboard; normalize the JSON.

### Python — mutmut

Declare mutmut in the project's existing dependency group and mutate an explicit path set rather than the
whole package tree. mutmut's command surface changed materially across major versions, so resolve the version
first and confirm the run, results, and export subcommands for it.

- **Scope** — explicit paths to mutate plus the project's real test command.
- **Changed code** — diff scoping is achieved by computing the changed paths and passing that set, rather than
  by a built-in since-reference flag.
- **Optimization** — a persistent result cache and parallel workers. Consider cosmic-ray instead when the
  suite is large enough that distributed execution matters.
- **Caveats** — a slow suite dominates runtime, because Python mutation cost scales with full test-process
  restarts. Keep the mutated scope small and the selected tests fast.
- **Report** — the tool's own result store, exportable to JUnit XML; normalize the export.

## Other ecosystems

Several other languages have maintained engines, including Rust, PHP, and Ruby. Where the project uses one,
apply the same rules: reuse existing configuration, scope by criticality and diff, and normalize into the
canonical report contract.

Report `NOT_SUPPORTED` with an explicit reason for technologies with no maintained mutation engine, including
mainframe and legacy source languages such as COBOL and PL/I, job control and scheduler definitions, database
schema and stored-procedure dialects without a mutation engine, configuration and infrastructure declarations,
and generated bindings. For those, state the compensating verification actually performed — characterization
or parity tests, contract tests, review, or reconciliation — and, when the work is a modernization, apply
mutation testing to the supported target implementation instead.

## Exclusions

Exclude the following from mutated scope by default, and record the exclusion in the run report:

- generated code, framework-generated bindings, and compiler or source-generator output;
- trivial accessors, data-transfer objects, and non-executable declarations;
- test code, fixtures, and test utilities;
- vendored or third-party sources the project does not own.

An exclusion is a recorded decision with a reason, not a silent narrowing of the denominator. Removing code
from scope to raise a score is a reporting defect.
