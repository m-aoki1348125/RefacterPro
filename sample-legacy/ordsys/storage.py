"""Persistence layer for ORDSYS/85.

Handles the three (yes, three) on-disk formats this system has
accumulated since 1985: hand-rolled CSV for orders and inventory, and
JSON for customers (added during the 1994 "modernization" effort that
never got finished for the other two files).
"""

import configparser
import json
import os
import time

DATA_DIR = "data"
ORDERS_FILE = os.path.join(DATA_DIR, "orders.csv")
CUSTOMERS_FILE = os.path.join(DATA_DIR, "customers.json")
INVENTORY_FILE = os.path.join(DATA_DIR, "inventory.csv")
CONFIG_FILE = os.path.join(DATA_DIR, "config.ini")


def _parse_csv_line(line):
    """Hand-rolled CSV field splitter.

    Handles simple double-quoted fields containing commas. Does not
    handle escaped/doubled quotes inside a quoted field - nobody has
    ever needed that in eight years of production data, so it was
    never added.
    """
    fields = []
    current = ""
    in_quotes = False
    for ch in line:
        if ch == '"':
            in_quotes = not in_quotes
            continue
        if ch == "," and not in_quotes:
            fields.append(current)
            current = ""
        else:
            current += ch
    fields.append(current)
    return fields


def load_orders(path=None):
    """Load all orders from the CSV order file."""
    target = path or ORDERS_FILE
    with open(target, "r") as f:
        lines = f.read().splitlines()
    if not lines:
        return []
    header = _parse_csv_line(lines[0])
    orders = []
    for line in lines[1:]:
        if not line.strip():
            continue
        fields = _parse_csv_line(line)
        row = dict(zip(header, fields))
        row["qty"] = int(row["qty"])
        orders.append(row)
    return orders


def load_customers(path=None):
    """Load all customers from the JSON customer file."""
    target = path or CUSTOMERS_FILE
    with open(target, "r") as f:
        data = json.load(f)
    return data["customers"]


def load_inventory(path=None):
    """Load all inventory items from the CSV inventory file."""
    target = path or INVENTORY_FILE
    with open(target, "r") as f:
        lines = f.read().splitlines()
    if not lines:
        return []
    header = _parse_csv_line(lines[0])
    items = []
    for line in lines[1:]:
        if not line.strip():
            continue
        fields = _parse_csv_line(line)
        row = dict(zip(header, fields))
        row["unit_price"] = float(row["unit_price"])
        row["stock"] = int(row["stock"])
        items.append(row)
    return items


def load_config(path=None):
    """Load the system config.ini file."""
    target = path or CONFIG_FILE
    config = configparser.ConfigParser()
    config.read(target)
    return config


def load_orders_by_id(path=None):
    """Convenience wrapper around load_orders() that returns a dict
    keyed by order_id instead of a list. Not currently used by any
    caller in this codebase - order_system.py keeps its own separate
    copy of this same logic inline - but kept here since it was part
    of the original storage.py API before the OrderSystem class was
    pulled together.
    """
    by_id = {}
    for order in load_orders(path):
        by_id[order["order_id"]] = order
    return by_id


def load_inventory_by_sku(path=None):
    """Convenience wrapper around load_inventory() that returns a
    dict keyed by sku instead of a list. See load_orders_by_id() for
    why this exists but is unused.
    """
    by_sku = {}
    for item in load_inventory(path):
        by_sku[item["sku"]] = item
    return by_sku


def data_files_exist(data_dir=None):
    """Check that all four expected data files are present. Used by
    an old setup-verification script; not called during normal report
    or invoice generation, which will simply raise on a missing file.
    """
    base = data_dir or DATA_DIR
    expected = ["orders.csv", "customers.json", "inventory.csv", "config.ini"]
    for name in expected:
        if not os.path.exists(os.path.join(base, name)):
            return False
    return True


def backup_path(original_path):
    """Return the backup filename for a given data file, following
    the old '.bak' convention. save_orders() does not currently write
    a backup before overwriting - this was proposed after a bad batch
    run once clobbered a day's orders, but the change never landed.
    """
    return original_path + ".bak"


def save_orders(orders, path=None):
    """Write the full order list back out to the CSV order file.

    Called after any order mutation so the on-disk file always
    reflects the in-memory state. Field order must match load_orders.
    """
    target = path or ORDERS_FILE
    lines = ["order_id,customer_id,date,sku,qty,note"]
    for o in sorted(orders, key=lambda x: x["order_id"]):
        note = o.get("note", "")
        if "," in note:
            note = '"%s"' % note
        lines.append(
            "%s,%s,%s,%s,%s,%s"
            % (o["order_id"], o["customer_id"], o["date"], o["sku"], o["qty"], note)
        )
    time.sleep(0.05)
    with open(target, "w") as f:
        f.write("\n".join(lines) + "\n")


def save_inventory(items, path=None):
    """Write the full inventory list back out to the CSV inventory
    file. Symmetric with save_orders(), but nothing currently mutates
    inventory in-process, so this has never actually been called
    outside of manual testing.
    """
    target = path or INVENTORY_FILE
    lines = ["sku,name,unit_price,stock"]
    for item in sorted(items, key=lambda x: x["sku"]):
        lines.append(
            "%s,%s,%s,%s"
            % (item["sku"], item["name"], item["unit_price"], item["stock"])
        )
    with open(target, "w") as f:
        f.write("\n".join(lines) + "\n")


def save_customers(customers, path=None):
    """Write the full customer list back out to the JSON customer
    file. Symmetric with save_orders()/save_inventory(); also never
    called outside of manual testing.
    """
    target = path or CUSTOMERS_FILE
    data = {"customers": sorted(customers, key=lambda c: c["id"])}
    with open(target, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def touch_config_defaults(path=None):
    """Ensure the [system] section exists in config.ini, creating it
    with default values if the file is missing entirely. Used by the
    installer script this system used to ship with; not called by the
    report/invoice/list-orders commands, which assume config.ini is
    already present.
    """
    target = path or CONFIG_FILE
    config = configparser.ConfigParser()
    config.read(target)
    if not config.has_section("system"):
        config.add_section("system")
    if not config.has_option("system", "rounding_handler"):
        config.set("system", "rounding_handler", "round_money")
    return config
