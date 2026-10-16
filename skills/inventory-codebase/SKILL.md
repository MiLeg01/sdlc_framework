---
name: inventory-codebase
description: Build a deterministic, bounded inventory of a repository or legacy source tree before interpretation. Use when the denominator, exclusions, classifications, hashes, batches, or drift must be established for broad analysis. Do not use for a small already-supplied file set, to infer behavior from paths, or as a substitute for source analysis.
---

# Inventory a codebase

Prove the denominator before making completeness claims.

## Procedure

1. Confirm the exact root, allowed scope, protected paths, exclusions, symlink policy, and output path.
2. Enumerate path metadata before reading contents. Prune VCS internals, dependencies, caches, build
   output, credentials, environment files, and explicitly protected directories.
3. Run:

   ```bash
   python3 scripts/inventory_codebase.py --root <root> --output <inventory.json> --hash
   ```

4. Review uncertain `other` classifications. Treat names and metadata as navigation clues, never
   behavioral evidence.
5. Give every eligible path one stable ID, classification, disposition, and reason. Retain unreadable
   items as failures rather than silently omitting them. Record both file-operation failures and
   directory-traversal failures through the walker's error callback, using repository-relative paths.
6. Create stable, non-overlapping analysis batches from sorted paths and subsystem/language boundaries. Keep
   legacy support artifacts such as copybooks, PL/I includes, CICS resource definitions, contracts, build
   descriptors, and runtime configuration eligible when they participate in the authorized system.
7. Reconcile eligible count, disposition count, and batch ownership. Store the exclusion policy and
   inventory fingerprint with the output.
8. When refreshing, compare path hashes; preserve IDs for unchanged files and mark changed analyzed
   items for review.

The output stores `root: .` by default so a committed inventory does not expose a username or workstation
path. Pass a synthetic repository-relative `--root-label` only when multiple authorized roots must be
distinguished.

## Failure rules

Fail on a wrong root, duplicate normalized paths/IDs, symlinks escaping the root, unreasoned omissions,
missing hashes when required, overlapping primary ownership, or any access to protected paths. Do not
infer authority, behavior, or completeness from filenames. Inventory metadata is not evidence.

## Completion

Complete only when every eligible path has one recorded disposition, counts reconcile, exclusions are
explicit, the fingerprint is reproducible, and stable non-overlapping batches cover the denominator. Naming a
first batch does not reduce the high-level `analyze-legacy-system` scope or authorize it to stop after that batch.
