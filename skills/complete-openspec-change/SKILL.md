---
name: complete-openspec-change
description: Safely complete and archive one verified OpenSpec change, merging or deliberately skipping spec deltas and confirming the archived state. Use only after implementation verification proves the change ready to close. Do not use with incomplete tasks, unresolved spec or code mismatches, failing required gates, ambiguous change selection, or research and presentation work without an OpenSpec software change.
---

# Complete an OpenSpec change

Archive is a lifecycle mutation: it updates the main specs when applicable and moves the active change into
history. Do not use OpenSpec's warning-tolerant archive behavior as permission to close incomplete work.

## Prove closure readiness

1. Resolve the exact active change; never infer among multiple candidates.
2. Read governance, OpenSpec configuration, current main specs, all change artifacts, implementation and test
   evidence, the latest independent verification result, Git state, and other active changes that could
   conflict with the same requirements.
3. Require all applicable artifacts and tasks complete, strict OpenSpec validation passing, required
   repository gates passing, and no unresolved critical mismatch or unapproved limitation.
4. For a no-behavior refactor or tooling/docs change, confirm `skip_specs: true` is intentional and that no
   delta specs conflict with it. Do not invent or merge behavior requirements.

## Complete the lifecycle

Use current project guidance and the installed OpenSpec version. Normally:

1. run `openspec validate <name> --strict --no-interactive` immediately before mutation;
2. inspect whether delta specs must be synced or will merge during archive;
3. archive the exact change with `openspec archive <name> --yes` when the user has authorized completion and
   no interactive terminal can answer confirmation;
4. do not use `--no-validate` to bypass a failing gate;
5. verify the dated archive destination exists, the active change no longer does, and main specs reflect all
   intended ADDED, MODIFIED, and REMOVED requirements;
6. run applicable post-archive validation, including `openspec validate --archived` where supported.

If the archive reports incomplete tasks, spec conflicts, validation errors, or a partial move, stop and
recover according to the command output. Do not report closure from an intended command alone.

## Return closure evidence

Report the archived change and destination, spec mutations or intentional skip, pre- and post-archive
commands/results, requirement and scenario completion summary, remaining limitations, and repository commit
or checkpoint when commits were authorized. The archived artifacts remain project-local audit history; do
not copy them into Agent Commons.
