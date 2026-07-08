"""Core order processing engine for ORDSYS/85.

This module holds the OrderSystem class, which is the entry point for
every command the CLI supports. It loads the order/customer/inventory
data, validates it, runs the pricing/discount/tax pipeline, and prints
the formatted reports and invoices. It was originally three separate
modules (loader, calculator, printer) that got merged together during
the 1996 "simplification" pass to "make things easier to find". They
have not been split back apart since.

Do not be alarmed by the size of this file. It has always been this
size, more or less, and every attempt to break it up has stalled out
partway through.
"""

import configparser
import csv
import json
import os

from ordsys import customers as customers_module
from ordsys import discounts
from ordsys import globalstate
from ordsys import inventory as inventory_module
from ordsys import legacy_compat
from ordsys import orders as orders_module
from ordsys import pricing
from ordsys import reports
from ordsys import tax
from ordsys import util

KNOWN_CUSTOMER_TYPES = ("GOLD", "STANDARD", "WHOLESALE")


class OrderSystem(object):
    """The ORDSYS/85 order processing engine.

    Handles file I/O, validation, pricing/discount/tax calculation,
    persistence, report formatting, and console output for the three
    supported commands: report, invoice, and list-orders.
    """

    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.orders_path = os.path.join(data_dir, "orders.csv")
        self.customers_path = os.path.join(data_dir, "customers.json")
        self.inventory_path = os.path.join(data_dir, "inventory.csv")
        self.config_path = os.path.join(data_dir, "config.ini")

        self._orders_cache = None
        self._customers_cache = None
        self._inventory_cache = None
        self._config_cache = None
        self._rounding_handler_cache = None

        globalstate.CACHE["order_system_initialized"] = 1

    # ------------------------------------------------------------------
    # Data loading
    #
    # These duplicate what storage.py already does. They were written
    # independently when this class was pulled together in 1996 and
    # nobody has gone back to make this class call storage.py instead.
    # ------------------------------------------------------------------

    def _load_orders(self):
        if self._orders_cache is not None:
            return self._orders_cache
        rows = []
        with open(self.orders_path, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["qty"] = int(row["qty"])
                rows.append(row)
        rows.sort(key=lambda r: r["order_id"])
        self._orders_cache = rows
        return rows

    def _load_customers(self):
        if self._customers_cache is not None:
            return self._customers_cache
        with open(self.customers_path, "r") as f:
            data = json.load(f)
        by_id = {}
        for c in data["customers"]:
            by_id[c["id"]] = c
        self._customers_cache = by_id
        return by_id

    def _load_inventory(self):
        if self._inventory_cache is not None:
            return self._inventory_cache
        by_sku = {}
        with open(self.inventory_path, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["unit_price"] = float(row["unit_price"])
                row["stock"] = int(row["stock"])
                by_sku[row["sku"]] = row
        self._inventory_cache = by_sku
        return by_sku

    def _load_config(self):
        if self._config_cache is not None:
            return self._config_cache
        config = configparser.ConfigParser()
        config.read(self.config_path)
        self._config_cache = config
        return config

    # ------------------------------------------------------------------
    # Validation
    #
    # Each field has its own check, copy-pasted from the previous one
    # and adjusted. This predates the idea of looping over a list of
    # (field, rule) pairs, and every time someone has proposed cleaning
    # it up the risk of breaking month-end has been judged too high.
    # ------------------------------------------------------------------

    def _validate_order_id(self, order):
        if "order_id" not in order or not order["order_id"]:
            raise ValueError("order missing order_id: %r" % (order,))
        if not order["order_id"].startswith("O-"):
            raise ValueError("order_id has bad format: %s" % order["order_id"])

    def _validate_order_customer(self, order):
        if "customer_id" not in order or not order["customer_id"]:
            raise ValueError("order missing customer_id: %r" % (order,))
        if not order["customer_id"].startswith("C-"):
            raise ValueError("customer_id has bad format: %s" % order["customer_id"])

    def _validate_order_date(self, order):
        if "date" not in order or not order["date"]:
            raise ValueError("order missing date: %r" % (order,))
        parts = order["date"].split("-")
        if len(parts) != 3:
            raise ValueError("date has bad format: %s" % order["date"])

    def _validate_order_sku(self, order):
        if "sku" not in order or not order["sku"]:
            raise ValueError("order missing sku: %r" % (order,))

    def _validate_order_qty(self, order):
        if "qty" not in order:
            raise ValueError("order missing qty: %r" % (order,))
        if order["qty"] <= 0:
            raise ValueError("qty must be positive: %s" % order["qty"])

    def _validate_order(self, order):
        self._validate_order_id(order)
        self._validate_order_customer(order)
        self._validate_order_date(order)
        self._validate_order_sku(order)
        self._validate_order_qty(order)

    def _validate_order_note(self, order):
        # note is optional, but if present it must not itself contain
        # a raw double-quote character - the CSV writer in storage.py
        # only knows how to wrap a note in quotes, not escape quotes
        # that are already inside one.
        note = order.get("note", "")
        if note and '"' in note:
            raise ValueError("order note contains an unescaped quote: %s" % order["order_id"])

    def _validate_all_orders(self):
        for order in self._load_orders():
            self._validate_order(order)
            self._validate_order_note(order)

    def _validate_customer_id(self, customer):
        if "id" not in customer or not customer["id"]:
            raise ValueError("customer missing id: %r" % (customer,))
        if not customer["id"].startswith("C-"):
            raise ValueError("customer id has bad format: %s" % customer["id"])

    def _validate_customer_name(self, customer):
        if "name" not in customer or not customer["name"]:
            raise ValueError("customer missing name: %r" % (customer,))

    def _validate_customer_type(self, customer):
        if "type" not in customer or not customer["type"]:
            raise ValueError("customer missing type: %r" % (customer,))
        if customer["type"] not in KNOWN_CUSTOMER_TYPES:
            raise ValueError("customer has unknown type: %s" % customer["type"])

    def _validate_customer(self, customer):
        self._validate_customer_id(customer)
        self._validate_customer_name(customer)
        self._validate_customer_type(customer)

    def _validate_all_customers(self):
        for customer in self._load_customers().values():
            self._validate_customer(customer)

    def _validate_inventory_sku(self, item):
        if "sku" not in item or not item["sku"]:
            raise ValueError("inventory item missing sku: %r" % (item,))

    def _validate_inventory_name(self, item):
        if "name" not in item or not item["name"]:
            raise ValueError("inventory item missing name: %r" % (item,))

    def _validate_inventory_price(self, item):
        if "unit_price" not in item:
            raise ValueError("inventory item missing unit_price: %r" % (item,))
        if item["unit_price"] < 0:
            raise ValueError("unit_price cannot be negative: %s" % item["unit_price"])

    def _validate_inventory_item(self, item):
        self._validate_inventory_sku(item)
        self._validate_inventory_name(item)
        self._validate_inventory_price(item)

    def _validate_all_inventory(self):
        for item in self._load_inventory().values():
            self._validate_inventory_item(item)

    # ------------------------------------------------------------------
    # Pricing / discount / tax pipeline
    # ------------------------------------------------------------------

    def _line_amount(self, customer_type, qty, unit_price):
        """Dispatch to the correct pricing routine for this customer
        type. See pricing.py for why there are three of these.
        """
        if customer_type == "GOLD":
            return pricing.calc_price_bulk([(qty, unit_price)])
        elif customer_type == "WHOLESALE":
            return pricing.calc_price_wholesale(qty, unit_price)
        else:
            return pricing.calc_price_standard(qty, unit_price)

    def _get_rounding_handler(self):
        """Resolve the final-rounding function to use for invoice and
        report totals, based on the rounding_handler setting in
        config.ini. Falls back to util.round_money if the config does
        not name a valid handler.
        """
        if self._rounding_handler_cache is not None:
            return self._rounding_handler_cache

        config = self._load_config()
        handler_name = "round_money"
        if config.has_option("system", "rounding_handler"):
            handler_name = config.get("system", "rounding_handler")

        if hasattr(legacy_compat, handler_name):
            handler = getattr(legacy_compat, handler_name)
        else:
            handler = util.round_money

        self._rounding_handler_cache = handler
        return handler

    def _compute_order_amount(self, order):
        """Compute the full billed amount for a single order.

        Runs the line pricing, applies the customer's account
        discount, applies sales tax for the order date, and rounds
        the final total using whatever handler config.ini selects.
        """
        customers_by_id = self._load_customers()
        inventory_by_sku = self._load_inventory()

        customer = customers_by_id[order["customer_id"]]
        item = inventory_by_sku[order["sku"]]

        subtotal = self._line_amount(customer["type"], order["qty"], item["unit_price"])

        discounted = discounts.apply_discount(customer["type"], subtotal)

        # Anniversary month bonus: as a thank-you, customers get their
        # loyalty discount applied again during the calendar month
        # they originally signed up in.
        since_yy_str, since_mm_str = customer["since"].split("-")
        order_yy, order_mm, order_dd = util.split_legacy_date(order["date"])
        if int(since_mm_str) == order_mm:
            discounted = discounts.apply_discount(customer["type"], discounted)

        date_int = tax.full_date_int(order_yy, order_mm, order_dd)
        rate = tax.tax_rate(date_int)
        taxed = discounted + (discounted * rate)

        handler = self._get_rounding_handler()
        final_amount = handler(taxed)

        return {
            "subtotal": subtotal,
            "discounted": discounted,
            "tax_amount": taxed - discounted,
            "total": final_amount,
        }

    # ------------------------------------------------------------------
    # Persistence
    #
    # Only used if an order is ever mutated in-process; none of the
    # three read-only CLI commands trigger this today, but it is kept
    # here since it is the OrderSystem's job to own the full order
    # lifecycle, not just reporting on it.
    # ------------------------------------------------------------------

    def persist_orders(self):
        from ordsys import storage

        storage.save_orders(self._load_orders(), self.orders_path)

    def _load_orders_legacy_fallback(self):
        """Hand-rolled order loader kept as a fallback for the period
        when this class was migrated from Python 2's csv module quirks
        to Python 3's. It mirrors storage.py's hand-rolled parser
        rather than the csv.DictReader-based _load_orders() above -
        a third independent implementation of the same fifteen lines
        of parsing logic. Not called anywhere; kept in case the
        csv.DictReader based path is ever found to disagree with it
        on some edge case nobody has hit yet.
        """
        rows = []
        with open(self.orders_path, "r") as f:
            lines = f.read().splitlines()
        if not lines:
            return rows
        header = [h.strip() for h in lines[0].split(",")]
        for line in lines[1:]:
            if not line.strip():
                continue
            values = line.split(",")
            row = dict(zip(header, values))
            if "qty" in row:
                row["qty"] = util.safe_int(row["qty"])
            rows.append(row)
        rows.sort(key=lambda r: r.get("order_id", ""))
        return rows

    def refresh_caches(self):
        """Drop all cached data so the next command re-reads from
        disk. Not called by report/invoice/list-orders (each CLI
        invocation is a fresh process anyway), but kept for callers
        embedding OrderSystem in a longer-running process, such as
        the old REPL-based admin console this system used to ship
        with.
        """
        self._orders_cache = None
        self._customers_cache = None
        self._inventory_cache = None
        self._config_cache = None
        self._rounding_handler_cache = None

    # ------------------------------------------------------------------
    # Commands
    # ------------------------------------------------------------------

    def cmd_report(self, month_str):
        """Print the monthly sales report for the given 'YYYY-MM' month."""
        self._validate_all_orders()
        self._validate_all_customers()
        self._validate_all_inventory()

        globalstate.CACHE["last_command"] = "report"

        legacy_month = util.yy_mm_from_full(month_str)
        customers_by_id = self._load_customers()

        matching = [o for o in self._load_orders() if o["date"][:5] == legacy_month]
        matching.sort(key=lambda o: o["order_id"])

        print(reports.report_header("ORDSYS/85 MONTHLY SALES REPORT\nMONTH: %s" % month_str))
        print()
        print(reports.format_row([("ORDER", 10, "l"), ("CUSTOMER", 30, "l"), ("AMOUNT", 15, "r")]))
        print(reports.THIN_LINE)

        grand_total = 0.0
        for order in matching:
            customer = customers_by_id[order["customer_id"]]
            amounts = self._compute_order_amount(order)
            grand_total += amounts["total"]
            print(reports.format_row([
                (order["order_id"], 10, "l"),
                (customer["name"], 30, "l"),
                (util.format_money(amounts["total"]), 15, "r"),
            ]))

        print(reports.THIN_LINE)
        print("TOTAL ORDERS: %d" % len(matching))
        print("TOTAL AMOUNT: %s" % util.format_money(grand_total))
        print(reports.report_footer())

    def cmd_invoice(self, order_id):
        """Print a single-order invoice for the given order id."""
        self._validate_all_orders()
        self._validate_all_customers()
        self._validate_all_inventory()

        globalstate.CACHE["last_command"] = "invoice"

        # Unlike cmd_report and cmd_list_orders above, the single-order
        # lookup here goes through the orders/customers/inventory
        # modules directly instead of the duplicate loaders - this was
        # the last part of OrderSystem touched before the 1996 merge
        # froze, so it never got converted over.
        order = orders_module.find_order(order_id)

        if order is None:
            print("ERROR: order not found: %s" % order_id)
            return

        customer = customers_module.find_customer(order["customer_id"])
        item = inventory_module.find_item(order["sku"])
        amounts = self._compute_order_amount(order)

        order_yy, order_mm, order_dd = util.split_legacy_date(order["date"])
        full_year = tax.expand_year(order_yy)
        full_date = "%04d-%02d-%02d" % (full_year, order_mm, order_dd)

        print(reports.report_header("ORDSYS/85 INVOICE"))
        print()
        print(reports.format_label_value("ORDER ID:", order["order_id"]))
        print(reports.format_label_value("CUSTOMER:", "%s (%s)" % (customer["name"], customer["type"])))
        print(reports.format_label_value("DATE:", full_date))
        print(reports.THIN_LINE)
        print(reports.format_row([
            ("ITEM", 9, "l"), ("DESCRIPTION", 24, "l"), ("QTY", 6, "r"),
            ("UNIT PRICE", 12, "r"), ("LINE TOTAL", 13, "r"),
        ]))
        print(reports.THIN_LINE)

        line_total = order["qty"] * item["unit_price"]
        print(reports.format_row([
            (item["sku"], 9, "l"), (item["name"], 24, "l"), (order["qty"], 6, "r"),
            (util.format_money(item["unit_price"]), 12, "r"), (util.format_money(line_total), 13, "r"),
        ]))

        print(reports.THIN_LINE)
        discount_amount = amounts["subtotal"] - amounts["discounted"]
        print(reports.format_row([("SUBTOTAL:", 58, "l"), (util.format_money(amounts["subtotal"]), 18, "r")]))
        print(reports.format_row([("DISCOUNT:", 58, "l"), (util.format_money(discount_amount), 18, "r")]))
        print(reports.format_row([("TAX:", 58, "l"), (util.format_money(amounts["tax_amount"]), 18, "r")]))
        print(reports.THIN_LINE)
        print(reports.format_row([("TOTAL:", 58, "l"), (util.format_money(amounts["total"]), 18, "r")]))
        print(reports.report_footer())

    def cmd_list_orders(self):
        """Print the full order list, one row per order."""
        self._validate_all_orders()
        self._validate_all_customers()

        globalstate.CACHE["last_command"] = "list-orders"

        customers_by_id = self._load_customers()
        all_orders = self._load_orders()

        print(reports.report_header("ORDSYS/85 ORDER LIST"))
        print()
        print(reports.format_row([
            ("ORDER", 9, "l"), ("CUSTOMER", 22, "l"), ("DATE", 11, "l"),
            ("SKU", 7, "l"), ("QTY", 5, "r"), ("TYPE", 10, "l"),
        ]))
        print(reports.THIN_LINE)

        for order in all_orders:
            customer = customers_by_id[order["customer_id"]]
            order_yy, order_mm, order_dd = util.split_legacy_date(order["date"])
            full_year = tax.expand_year(order_yy)
            full_date = "%04d-%02d-%02d" % (full_year, order_mm, order_dd)
            print(reports.format_row([
                (order["order_id"], 9, "l"), (customer["name"], 22, "l"), (full_date, 11, "l"),
                (order["sku"], 7, "l"), (order["qty"], 5, "r"), (customer["type"], 10, "l"),
            ]))

        print(reports.THIN_LINE)
        print("TOTAL: %d orders" % len(all_orders))
        print(reports.report_footer())
