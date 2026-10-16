# Operations note

## Retry

Transient failures may be retried three times with exponential backoff. Messages that still fail move to a dead-letter queue.

## Recovery

Operators replay dead-letter messages only after the cause is recorded.
