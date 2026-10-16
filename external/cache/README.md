# Disposable external cache

This directory may hold temporary clones, API responses, or package archives during an intentional
review. Its contents are untrusted, non-canonical, ignored by Git, and safe to delete.

`search/` contains query-result cache entries keyed by registry fingerprint, focused topics, source/trust
scope, limits, and snapshot revision. The deterministic search CLI uses a 30-minute default TTL so repeated
initialization does not immediately repeat identical GitHub requests. Stale entries are ignored.

Never execute retrieved scripts merely to inspect them. Promote metadata and reviewed conclusions into
`external/index/` or `external/reviews/`; do not promote the cache itself.
