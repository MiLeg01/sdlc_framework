# Deterministic execution plan

The planner accepts a JSON object:

```json
{
  "schema_version": 1,
  "max_concurrency": 3,
  "tasks": [
    {
      "id": "bounded-task",
      "dependencies": ["prerequisite-task"],
      "write_paths": ["isolated/output/path"],
      "shared_surfaces": ["canonical:requirements"]
    }
  ]
}
```

- Task IDs are unique and dependencies must resolve to another task.
- `write_paths` are exact portable repository-relative paths without globs or parent traversal. Parent and
  child paths conflict because either worker could mutate the same subtree.
- `shared_surfaces` are stable coordinator-defined names for mutable state that path comparison cannot
  protect, such as a main specification, schema, lockfile, database migration sequence, test database,
  service port, Git index, external state, or canonical registry. Equal names conflict.
- `max_concurrency` is a positive upper bound, not a target.

Run `python3 tools/plan_parallel_execution.py <plan.json>`. The output contains a serialized `stages` array.
Tasks inside one stage may run concurrently; stages run in order. A task may be deferred because the stage
reached its concurrency bound or because another selected task owns a conflicting path or shared surface.
The separate `conflicts` array makes all detected ownership collisions visible even when dependencies already
serialize the tasks.

The helper detects structural scheduling conflicts only. The coordinator still decides whether work is
semantically independent, whether runtime isolation is credible, and whether integration and validation
results authorize dependent work.
