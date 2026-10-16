"""Weak suite: every test passes, yet meaningful mutants survive.

This is the deliberate "before" state of the benchmark. The tests exercise only comfortable
mid-range values, so no boundary, no rejection path, and no reduced-rate branch is asserted.
"""

import unittest

from tax_calculator import apply_discount, invoice_total, tax_rate


class WeakTaxCalculatorTests(unittest.TestCase):
    def test_standard_rate_applies_to_a_large_amount(self):
        self.assertEqual(tax_rate(500.00), 0.20)

    def test_discount_reduces_the_net_amount(self):
        self.assertEqual(apply_discount(200.00, 0.10), 180.00)

    def test_invoice_total_includes_tax(self):
        self.assertEqual(invoice_total(200.00), 240.00)

    def test_discounted_invoice_total(self):
        self.assertEqual(invoice_total(200.00, 0.10), 216.00)


if __name__ == "__main__":
    unittest.main()
