"""Regression tests carried over from the original ORDSYS/85 Python
port. Nobody has looked closely at these in years. Do not delete.
"""

import unittest

from ordsys import tax
from ordsys import util


class TestLegacyMath(unittest.TestCase):

    def test_round_money_basic(self):
        self.assertEqual(util.round_money(10.0), 10.0)
        self.assertEqual(util.round_money(19.995), 20.0)

    def test_expand_year_window(self):
        self.assertEqual(tax.expand_year(86), 1986)
        self.assertEqual(tax.expand_year(5), 2005)

    def test_tax_rate_modern(self):
        # The sales tax rate has been 3% since the 1989 reform and
        # nothing has changed it since. This should still hold today.
        self.assertEqual(tax.tax_rate(19980101), 0.03)


if __name__ == "__main__":
    unittest.main()
