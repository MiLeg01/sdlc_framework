"""Hardened suite: the weak suite plus the behavioral tests the survivors demanded.

Each added test came from one classified survivor and asserts observable behavior required by an
acceptance criterion. None of them assert private details, call sequencing, or arbitrary constants.
"""

import unittest

from tax_calculator import apply_discount, invoice_total, tax_rate


class HardenedTaxCalculatorTests(unittest.TestCase):
    def test_standard_rate_applies_to_a_large_amount(self):
        self.assertEqual(tax_rate(500.00), 0.20)

    def test_discount_reduces_the_net_amount(self):
        self.assertEqual(apply_discount(200.00, 0.10), 180.00)

    def test_invoice_total_includes_tax(self):
        self.assertEqual(invoice_total(200.00), 240.00)

    def test_discounted_invoice_total(self):
        self.assertEqual(invoice_total(200.00, 0.10), 216.00)

    # MUT-001, AC-004-3: the threshold itself belongs to the standard rate.
    def test_reduced_rate_boundary_is_exclusive_at_the_threshold(self):
        self.assertEqual(tax_rate(99.99), 0.10)
        self.assertEqual(tax_rate(100.00), 0.20)
        self.assertEqual(tax_rate(100.01), 0.20)

    # MUT-002, AC-004-1: the maximum discount rate is accepted, and anything above it is rejected.
    def test_maximum_discount_rate_is_inclusive(self):
        self.assertEqual(apply_discount(200.00, 0.30), 140.00)
        with self.assertRaises(ValueError):
            apply_discount(200.00, 0.31)

    # MUT-003, AC-004-1: a negative discount rate is rejected rather than inflating the invoice.
    def test_negative_discount_rate_is_rejected(self):
        with self.assertRaises(ValueError):
            apply_discount(200.00, -0.50)


if __name__ == "__main__":
    unittest.main()
