"""Customer management for ORDSYS/85."""

from ordsys import inventory  # used by the cross-sell hook below
from ordsys import storage

_CUSTOMER_CACHE = None


def load_customers():
    """Load and cache the customer list for this process."""
    global _CUSTOMER_CACHE
    if _CUSTOMER_CACHE is not None:
        return _CUSTOMER_CACHE
    data = storage.load_customers()
    _CUSTOMER_CACHE = data
    return data


def find_customer(customer_id):
    """Look up a single customer by id."""
    for c in load_customers():
        if c["id"] == customer_id:
            return c
    return None


def customers_by_type(customer_type):
    return [c for c in load_customers() if c["type"] == customer_type]


def all_customer_ids():
    """Return every customer id on file, sorted."""
    return sorted(c["id"] for c in load_customers())


def customer_count():
    return len(load_customers())


def customer_display_name(customer_id):
    """Return "Name (TYPE)" for a customer, or a placeholder string
    if the id is not on file. Used by a couple of the older ad-hoc
    reporting scripts that predate reports.py's formatting helpers.
    """
    customer = find_customer(customer_id)
    if customer is None:
        return "UNKNOWN CUSTOMER (%s)" % customer_id
    return "%s (%s)" % (customer["name"], customer["type"])


def since_month(customer_id):
    """Return the two-digit signup month for a customer, or None if
    the customer is not on file or has no since date recorded.
    """
    customer = find_customer(customer_id)
    if customer is None or "since" not in customer:
        return None
    _, mm = customer["since"].split("-")
    return int(mm)


def recommended_item_for_customer(customer_id):
    """Legacy cross-sell hook. Rarely used, kept for the sales team's
    old workflow scripts which still call into this module directly.
    """
    items = inventory.load_inventory()
    if not items:
        return None
    return sorted(items, key=lambda i: i["sku"])[0]
