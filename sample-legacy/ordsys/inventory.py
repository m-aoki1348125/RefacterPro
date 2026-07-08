"""Inventory management for ORDSYS/85."""

from ordsys import storage

_INVENTORY_CACHE = None


def load_inventory():
    """Load and cache the inventory list for this process."""
    global _INVENTORY_CACHE
    if _INVENTORY_CACHE is not None:
        return _INVENTORY_CACHE
    items = storage.load_inventory()
    _INVENTORY_CACHE = items
    return items


def find_item(sku):
    """Look up a single inventory item by SKU."""
    for item in load_inventory():
        if item["sku"] == sku:
            return item
    return None


def in_stock(sku, qty):
    item = find_item(sku)
    if item is None:
        return False
    return item["stock"] >= qty


def all_skus():
    """Return every SKU currently on file, sorted."""
    return sorted(item["sku"] for item in load_inventory())


def low_stock_items(threshold):
    """Return all inventory items whose stock is at or below the
    given threshold, sorted by SKU. Used by a reorder-point report
    that is not currently exposed through the CLI.
    """
    matches = [item for item in load_inventory() if item["stock"] <= threshold]
    return sorted(matches, key=lambda i: i["sku"])


def total_stock_value():
    """Return the total value of on-hand inventory (unit_price * stock,
    summed across every item). Used by an old end-of-quarter asset
    report; not wired into the current report/invoice/list-orders
    commands.
    """
    total = 0.0
    for item in load_inventory():
        total += item["unit_price"] * item["stock"]
    return total


def units_sold_for_sku(sku):
    """Total quantity sold to date for a given SKU, across all orders.

    Used by the (rarely run) reorder-point report.
    """
    # import here to avoid import error at startup
    from ordsys import orders

    total = 0
    for o in orders.load_all_orders():
        if o["sku"] == sku:
            total += o["qty"]
    return total
