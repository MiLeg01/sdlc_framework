---
name: review-privacy-security
description: Review a system, design, change, or workflow for privacy and security using evidence-backed data-flow mapping, trust boundaries, abuse paths, minimization, secrets, logging, retention, isolation, negative tests, and claim limits. Use before consequential delivery or when sensitive data and privileged operations are in scope. Do not use as a compliance certification, a substitute for authorized penetration testing, or an implementation task presented as independent review.
---

# Review privacy and security

Establish scope, assets, actors, data classes, environments, applicable policies, deployment assumptions,
and evidence access. State what is outside the review.

## Model the system

1. Trace collection, ingress, parsing, validation, transformation, storage, caching, logging, analytics,
   sharing, export, retention, deletion, and recovery of sensitive data.
2. Mark trust boundaries, identities, authorization decisions, tenant or workload isolation, secrets,
   network calls, parsers, file handling, administrative paths, and third-party dependencies.
3. Separate verified controls, inferred controls, proposed controls, conflicts, and unknowns.

## Challenge the design and implementation

Assess data minimization, purpose limitation, defaults, consent or authority, access control, secret
handling, redaction, encryption assumptions, retention, deletion, auditability, isolation, injection,
request forgery, traversal, unsafe deserialization, dependency risk, denial of service, replay, race,
idempotency, failure handling, and recovery. Adapt the threat set to the actual surface.

Use negative tests and concrete abuse paths. Verify that logs, errors, telemetry, fixtures, backups, and
generated artifacts do not quietly reintroduce protected data or credentials.

## Report

Return a scoped system and data-flow summary, assumptions, evidence, severity-ranked findings, affected
assets and actors, reproduction or attack path, existing controls, recommended control class, validation
needed, residual risk, and review limitations. Do not claim a control exists without evidence or convert an
unreachable environment into a pass.

For consequential work, delegate this workflow to the independent `privacy-security-reviewer`. The reviewer
finds and challenges; the implementation owner decides and applies fixes through normal authorized workflows.
