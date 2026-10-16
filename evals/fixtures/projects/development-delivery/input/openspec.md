# SPEC-AUTH-003

Scenario: reject an expired session

- Given a session whose expiry precedes the current instant
- When validation runs
- Then the result is `SESSION_EXPIRED`

Scenario: accept an active session

- Given a session whose expiry follows the current instant
- When validation runs
- Then the result is `ACTIVE`
