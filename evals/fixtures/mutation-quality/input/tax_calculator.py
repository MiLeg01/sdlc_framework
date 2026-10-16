"""Invoice totalling with a reduced-rate threshold and a validated discount.

Synthetic business-rule fixture for the mutation-testing benchmark. The rules below stand in for
REQ-017 / SPEC-004:

- AC-004-1  a discount rate outside the inclusive range 0.00 to 0.30 is rejected;
- AC-004-2  the discounted net amount is rounded to two decimal places;
- AC-004-3  a discounted net amount below 100.00 attracts the reduced rate, and 100.00 itself
            attracts the standard rate.
"""

REDUCED_RATE = 0.10
STANDARD_RATE = 0.20
REDUCED_RATE_THRESHOLD = 100.00
MAX_DISCOUNT_RATE = 0.30


def tax_rate(net_amount):
    """Return the tax rate for a discounted net amount (AC-004-3)."""
    if net_amount < REDUCED_RATE_THRESHOLD:
        return REDUCED_RATE
    return STANDARD_RATE


def apply_discount(net_amount, discount_rate):
    """Return the discounted net amount, rejecting an out-of-range rate (AC-004-1, AC-004-2)."""
    if discount_rate < 0 or discount_rate > MAX_DISCOUNT_RATE:
        raise ValueError("discount rate out of range")
    return round(net_amount * (1 - discount_rate), 2)


def invoice_total(net_amount, discount_rate=0.0):
    """Return the gross invoice total for a net amount and discount rate."""
    discounted = apply_discount(net_amount, discount_rate)
    return round(discounted + discounted * tax_rate(discounted), 2)
