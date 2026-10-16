# External capability review report contract

Canonical reviews use scalar frontmatter compatible with `external/schema/review.schema.json`, followed by:

1. review boundary and evidence;
2. provenance;
3. license assessment;
4. security and supply-chain characteristics;
5. semantic comparison with current commons;
6. useful novel patterns;
7. rejected or non-canonical patterns;
8. promotion candidates;
9. required evaluations before promotion;
10. final recommendation.

Required frontmatter fields:

```text
schema_version
id
source_id
repository
path
revision
trust
license
license_scope
security_class
relationship
status
reviewed_at
```

Use only the lifecycle states defined by the external index. A reviewed item must link to the same candidate
ID and revision in `external/index/capabilities.json`. An upstream change makes the review `OUTDATED`; it
does not rewrite the historical review.

For license claims, use cautious language such as "appears to permit" and record uncertainty. For security,
list observed executable surfaces and state what was not executed. For promotion, distinguish a reusable
idea from copied wording, code, assets, or package structure.
