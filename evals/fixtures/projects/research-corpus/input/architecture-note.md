# Architecture note

## Delivery

The consumer is idempotent by request identifier. The broker provides at-least-once delivery.

## Ordering

Ordering is required only within one customer account.
