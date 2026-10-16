---
name: create-sequence-diagram
description: Trace and validate an interaction over time as participants, ordered messages, activations, alternatives, loops, asynchronous events, and failures. Use for API requests, authentication, business processes, legacy call chains, service interactions, error paths, or current-versus-target flow comparisons when ordering matters. Do not use for static dependency maps, unsupported branches, or a flow reconstructed only from participant names without tracing code, contracts, logs, or specifications.
---

# Create a sequence diagram

Choose one bounded scenario and make time/order the primary dimension. Apply the shared protocol from
`create-technical-diagram`.

## Trace the interaction

1. Define the trigger, preconditions, completion condition, happy path, requested alternatives, error
   paths, and current/target state.
2. Identify actors, clients, services, components, stores, queues, and external systems from source,
   contracts, traces, logs, tests, or authoritative specifications.
3. Trace calls and messages in order. Record direction, operation/event, sync versus async behavior,
   returned result, persistence, retries, timeouts, and transaction boundaries when evidenced.
4. Add `alt`, `opt`, `loop`, parallel, and error fragments only when supported. Keep uncertain ordering or
   dynamic dispatch explicit rather than choosing a convenient sequence.

Separate current and target sequences when combining them would confuse observed and proposed behavior.
For a long interaction, create an overview sequence and focused subsequences around major phases.

Mermaid and PlantUML are usually appropriate editable formats; native SVG/HTML is useful when presentation
styling or responsive annotations matter.

## Validate

Reconcile every participant and message to a source locator or approved scenario. Verify ordering,
direction, sync/async semantics, alternatives, error propagation, return values, and termination. Ensure
the diagram does not imply calls merely because components are statically related. Return editable source,
rendered output, evidence metadata, scenario/precondition notes, legend, and unknowns.
