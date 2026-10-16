# Normalized implementation queue

The ranking helper accepts a JSON array or `{ "items": [...] }`. Each item uses:

- `id` (required, unique string)
- `status`: `ready`, `planned`, `in_progress`, `done`, or `blocked`
- `priority`: `must`, `should`, `could`, or `wont`
- `dependencies`: IDs that must be done
- `risk`: integer 0-10
- `acceptance_criteria`: array or integer count
- `evidence_confidence`: `high`, `medium`, `low`, or `unknown`
- `decision_blocked`: boolean
- `externally_owned`: boolean
- `active_claim`: boolean
- `write_paths`: exact portable relative paths exclusively owned while the slice runs
- `shared_surfaces`: mutable coordinator-defined resources that must not overlap in one execution stage
- `base_revision`: immutable revision from which an isolated worker starts
- `isolation_id`: worktree, branch, task-directory, or equivalent transaction identity
- `resource_leases`: ports, databases, caches, containers, or other runtime namespaces reserved to the slice

The helper rejects duplicate IDs, removes done/blocked/claimed/external work, checks dependencies, and
ranks priority, readiness, lower risk/scope, stronger evidence, then stable ID. Its output is a shortlist;
semantic review remains mandatory.

The ranking helper does not prove concurrency safety. Export shortlisted tasks to the deterministic parallel
execution planner with their dependencies, `write_paths`, and `shared_surfaces`. Missing isolation or lease
information keeps a writable slice sequential even when its file paths appear disjoint.
