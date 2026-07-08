"""Pricing calculations for ORDSYS/85.

Three near-identical routines live here. Ask around and nobody quite
remembers why there are three separate functions instead of one -
the story goes that wholesale pricing was bolted on by a different
team in the early 90s and it was easier to add a new function than
to touch the existing ones. Changing any of them tends to shift
month-end totals, so they have been left alone ever since.
"""

import math

from ordsys import util


def calc_price_standard(qty, unit_price):
    """Standard retail line pricing."""
    raw = qty * unit_price
    return util.round_money(raw)


def calc_price_bulk(items):
    """Bulk pricing across a list of (qty, unit_price) line items.

    Used for GOLD account orders, which are billed as a single
    combined line regardless of how many SKUs are on the order.
    """
    total = 0.0
    for qty, unit_price in items:
        total += qty * unit_price
    return util.round_money(total)


def calc_price_wholesale(qty, unit_price):
    """Wholesale line pricing."""
    raw = qty * unit_price
    return math.floor(raw * 100) / 100.0


def calc_price_legacy_v1(qty, unit_price):
    """Original 1985 pricing routine, superseded by calc_price_standard
    when unit pricing moved to floating point in the Python port.
    Kept here, unused, because a previous attempt to delete it broke
    an off-site batch script that imported it directly by name. Do
    not call this from any new code.
    """
    cents = int(round(qty * unit_price * 100))
    return cents / 100.0


def calc_price_summary(order_lines):
    """Sum a list of already-computed line prices into an order total.

    order_lines is a list of floats, each already run through one of
    the calc_price_* functions above. This does not itself apply any
    rounding - callers are expected to round the final total
    separately, same as everywhere else in this codebase.
    """
    total = 0.0
    for line_price in order_lines:
        total += line_price
    return total


def line_price_for_customer_type(customer_type, qty, unit_price):
    """Convenience dispatcher mirroring the logic in
    OrderSystem._line_amount. Not currently called from order_system.py
    (which keeps its own copy inline) - kept here for backward
    compatibility with older standalone reporting scripts that predate
    the CLI rewrite and imported this module directly.
    """
    if customer_type == "GOLD":
        return calc_price_bulk([(qty, unit_price)])
    elif customer_type == "WHOLESALE":
        return calc_price_wholesale(qty, unit_price)
    return calc_price_standard(qty, unit_price)
