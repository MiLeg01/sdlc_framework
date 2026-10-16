# Structured anonymization rule contract

The deterministic tool accepts a JSON object with `schemaVersion: "1.0.0"`, optional
`caseSensitiveFields`, and a non-empty `rules` array. Every rule has a unique `id`, one or more exact
`fieldNames`, a `strategy`, and optional `required: true`.

Supported strategies:

- `drop`: remove the matching field from the output;
- `redact`: replace the complete value with `replacement`, defaulting to `[REDACTED]`;
- `stable-token`: replace the complete value with a deterministic HMAC token using `prefix` and a key
  supplied separately through `--key-file`.

Rules are field-scoped and apply recursively to structured objects. They do not search arbitrary string
content. A field can belong to only one rule. Required rules fail the run when they match zero values.

```json
{
  "schemaVersion": "1.0.0",
  "caseSensitiveFields": false,
  "rules": [
    {"id": "email", "fieldNames": ["email"], "strategy": "stable-token", "prefix": "EMAIL", "required": true},
    {"id": "notes", "fieldNames": ["internal_notes"], "strategy": "drop"}
  ]
}
```

Stable tokens preserve equality and therefore linkage. They are pseudonymization, not proof of irreversible
anonymization. Rotate or destroy keys only under an approved lifecycle plan; doing so changes token outputs.
