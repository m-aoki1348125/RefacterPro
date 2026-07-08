"""Order management for ORDSYS/85."""

from ordsys import customers
from ordsys import globalstate
from ordsys import storage

_ORDERS_CACHE_KEY = "all_orders"


def load_all_orders():
    """Load and cache all orders for this process, sorted by order id."""
    if _ORDERS_CACHE_KEY in globalstate.CACHE:
        return globalstate.CACHE[_ORDERS_CACHE_KEY]
    data = sorted(storage.load_orders(), key=lambda o: o["order_id"])
    globalstate.CACHE[_ORDERS_CACHE_KEY] = data
    if globalstate.FLAGS["verbose"]:
        print("loaded %d orders" % len(data))
    return data


def find_order(order_id):
    """Look up a single order by id."""
    for o in load_all_orders():
        if o["order_id"] == order_id:
            return o
    return None


def orders_for_legacy_month(yy_mm):
    """Return all orders whose date falls in the given 'YY-MM' month,
    sorted by order id.
    """
    result = []
    for o in load_all_orders():
        if o["date"][:5] == yy_mm:
            result.append(o)
    return sorted(result, key=lambda o: o["order_id"])


def orders_for_customer(customer_id):
    result = [o for o in load_all_orders() if o["customer_id"] == customer_id]
    return sorted(result, key=lambda o: o["order_id"])


def customer_for_order(order):
    """Convenience join back to the owning customer record."""
    return customers.find_customer(order["customer_id"])


def count_orders():
    return len(load_all_orders())


def total_qty_for_customer(customer_id):
    """Sum of qty across all orders placed by a given customer.
    Used by an old sales-volume script; not currently wired into the
    report/invoice/list-orders commands.
    """
    total = 0
    for o in orders_for_customer(customer_id):
        total += o["qty"]
    return total


def orders_between(start_yy_mm, end_yy_mm):
    """Return all orders with a legacy 'YY-MM' date prefix between
    start_yy_mm and end_yy_mm inclusive, using plain string
    comparison. Only valid within a single decade window since it
    does not account for year rollover - fine for the historical data
    this system has always dealt with, but would misbehave across a
    99-to-00 boundary. Nobody has hit that yet.
    """
    result = []
    for o in load_all_orders():
        prefix = o["date"][:5]
        if start_yy_mm <= prefix <= end_yy_mm:
            result.append(o)
    return sorted(result, key=lambda o: o["order_id"])


def skus_ordered():
    """Return the sorted set of every SKU that appears in at least
    one order.
    """
    skus = set()
    for o in load_all_orders():
        skus.add(o["sku"])
    return sorted(skus)
