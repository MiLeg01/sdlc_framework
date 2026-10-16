---
name: protect-git-work
description: Preserve and recover repository work through explicit dirty-state ownership, staged-diff review, secret checks, bounded checkpoints, safe integration conditions, abort rules, and exact handoff from a verified Git state. Use before or during substantial edits, rebases, merges, migrations, or multi-contributor work. Do not use to erase unknown changes, rewrite shared history without authorization, bypass repository policy, or treat an unverified commit as a safe checkpoint.
---

# Protect Git work

Treat every pre-existing change as owned until proven otherwise.

## Establish state

1. Resolve repository root, branch, HEAD, upstream, worktrees, status, staged and unstaged diffs, untracked
   files, conflicts, active operations, and relevant recent commits.
2. Classify changes as task-owned, user-owned, collaborator-owned, generated, ignored, or unknown. Do not
   absorb unknown work into the task.
3. Record protected paths, shared-history constraints, hooks, required gates, and the accepted recovery point.

## Work and checkpoint

Use narrow edits and review the exact diff before staging. Stage explicit paths or hunks, then inspect the
staged diff, unexpected binaries, generated changes, credentials, tokens, private keys, personal data, and
large-file policy. Run the validation appropriate to the checkpoint.

Create bounded commits only when authorized. A checkpoint records purpose, paths, validation, known failures,
and recovery command; it must not mix unrelated ownership. Tags, branches, stashes, patches, or worktrees may
be safer than a commit depending on policy and sharing.

## Integrate and recover

Before merge, rebase, cherry-pick, or history editing, require a known base, clean ownership boundary, backup
or recoverable reference, and explicit shared-history authorization. Abort on unexpected target drift,
unowned conflicts, secret exposure, validation regression, unclear upstream, or an operation whose recovery
has not been proven.

After integration, verify HEAD, status, diff, ancestry, and required tests. Hand off the exact commit or
reference, remaining dirty paths and owners, validation evidence, blockers, and one recovery or continuation
action. Never use destructive cleanup merely to make status look clean.
