# Deterministic extraction contract

Run `scripts/extract_legacy_structure.py` only after the inventory establishes authorized source paths.
It accepts COBOL, Java, and SQL files and emits JSON with source hash, language, exact coordinates,
lexical observations, unresolved dynamic constructs, and limitations.

Treat the output as navigation and structural evidence, not as a semantic call graph. Reconcile hashes and
coordinates before use, deduplicate generated or copied sources, follow unresolved edges manually, and cite
the original source rather than the extractor as authority. Unsupported dialects and preprocessing remain
explicit gaps; do not silently reinterpret them with another language mode.
