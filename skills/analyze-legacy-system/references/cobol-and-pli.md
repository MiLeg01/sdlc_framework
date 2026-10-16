# COBOL and PL/I analysis

- Resolve program IDs, entry linkage, copy/include expansion, data areas, paragraphs/sections, external
  calls, file/database access, and batch control before interpreting rules.
- Trace meaningful paths from entry through sections/procedures, branches, loops, data operations, calls,
  outputs, exceptional exits, and side effects. Record rules with stable IDs and exact conditions,
  calculations, exceptions, affected data, and evidence rather than saying only that validation exists.
- Record paragraph reachability and unresolved dynamic calls. A paragraph name is not a business rule.
- Trace variable lineage through moves, redefines/overlays, condition names, arithmetic, tables/arrays,
  file records, copybook fields, and outputs.
- Treat copybooks/includes as shared structure whose semantics depend on each use context.
- Analyze field nesting, types/sizes, condition names, arrays/OCCURS, overlays/REDEFINES, keys, mappings,
  validation, transformations, and semantic differences across COBOL, PL/I, contracts, and target models.
- Separate online transactions, batch/JCL steps, utilities, generated code, test drivers, and dead or
  uncertain paths.
- For migrations, establish golden inputs/outputs and first divergence; do not translate syntax alone.
