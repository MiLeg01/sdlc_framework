# Synthetic order platform architecture

## Scope

The reviewed change adds synchronous billing authorization to the existing order checkout path.

## Components and ownership

- `PublicClient` calls `ApiGateway` over HTTPS.
- `ApiGateway` calls `OrderService` over HTTPS. The Edge team owns `ApiGateway`; the Orders team owns `OrderService`.
- `OrderService` calls `BillingService` synchronously over HTTPS. The Payments team owns `BillingService`.
- `OrderService` and `BillingService` both write the `order_status` table in `OrdersDb`; no single team owns the shared schema.
- `BillingService` calls `OrderService` synchronously to confirm authorization, creating a request cycle.

## State and failure behavior

`OrderService` writes `PENDING` before authorization and `CONFIRMED` after a successful response. A timeout leaves
`PENDING` rows without an automated reconciliation path. Retries carry no idempotency key, so duplicate charges
are possible. The proposal has no rollback or staged-migration plan for the shared schema.
