# Sequence diagram pattern

- Best use: one bounded scenario where participant ordering, messages, alternatives, or failures matter.
- Avoid: static topology, unrelated scenarios, or branches that are not supported by evidence.
- Structure: actor/client left, internal participants next, stores/queues/external systems right; keep time
  vertical and fragments narrow.
- Capacity: 3-9 participants and roughly 8-25 messages. Split long phases into overview and subsequences.
- Branching: label conditions and outcomes; distinguish sync calls, async messages, returns, retries, and timeouts.
- Responsive: transform into an ordered message table grouped by phase and branch.
- Accessibility: number messages and include sender, receiver, operation, condition, and result in text.
