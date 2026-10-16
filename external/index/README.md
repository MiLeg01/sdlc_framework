# External capability index

`capabilities.json` is a small metadata index of deliberately retained discoveries. It is not a package
manager, lockfile, installed skill directory, or mirror. Entries remain inactive and untrusted until a
review says otherwise, and even reviewed entries do not modify canonical commons automatically.

Use `python3 tools/external_capabilities.py validate` after editing and
`python3 tools/external_capabilities.py check-stale` to compare pinned revisions with current upstream
heads. A stale check marks review currency; it never overwrites the original review.
