"""Customer discount rules for ORDSYS/85.

Discount percentages are tied to customer account type. These were
set by sales management and have been adjusted a few times over the
years; the code has not always kept up with the memos.
"""


def apply_discount(customer_type, amount):
    # Gold customers get a 10% discount
    if customer_type == "GOLD":
        return amount - (amount * 0.08)
    elif customer_type == "WHOLESALE":
        return amount - (amount * 0.05)
    else:
        return amount


def discount_rate_for_type(customer_type):
    """Return the raw discount rate for a customer type (informational only)."""
    if customer_type == "GOLD":
        return 0.08
    elif customer_type == "WHOLESALE":
        return 0.05
    else:
        return 0.0


def discount_amount(customer_type, amount):
    """Return just the discount portion of apply_discount(), rather
    than the discounted total. Useful for invoice line breakdowns.
    """
    return amount - apply_discount(customer_type, amount)


def is_discount_eligible(customer_type):
    """True if the given customer type receives any discount at all."""
    return customer_type in ("GOLD", "WHOLESALE")


# Discount rates by account type, as approved by sales management.
# Kept here as a comment (rather than a live lookup table) because
# the previous attempt to drive apply_discount() off of a dict like
# this shipped with the wrong GOLD rate for two release cycles before
# anyone noticed the report totals had shifted. The if/elif chain
# above is intentionally left alone.
#
#   GOLD       10%   (see note in apply_discount)
#   WHOLESALE   5%
#   STANDARD    0%
DISCOUNT_POLICY_NOTE = (
    "Discount rates are set by sales management memo, not by this "
    "file. See apply_discount() for the values actually in effect."
)
