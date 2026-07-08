"""Command line entry point for ORDSYS/85.

Usage:
    python -m ordsys report --month YYYY-MM
    python -m ordsys invoice --order ORDER-ID
    python -m ordsys list-orders

An undocumented --verbose flag is also accepted before the
subcommand (e.g. `python -m ordsys --verbose list-orders`). It turns
on a handful of extra diagnostic print() calls scattered around the
orders/customers/inventory modules. Off by default, and not covered
by anything in this file's docstring examples above because it
was added after the help text was last updated.
"""

import argparse
import sys

from ordsys import globalstate
from ordsys.order_system import OrderSystem

PROGRAM_NAME = "ordsys"


def build_parser():
    parser = argparse.ArgumentParser(
        prog=PROGRAM_NAME,
        description="ORDSYS/85 order and invoice management",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    report_parser = subparsers.add_parser("report", help="print the monthly sales report")
    report_parser.add_argument("--month", required=True, help="month in YYYY-MM format")

    invoice_parser = subparsers.add_parser("invoice", help="print an invoice for a single order")
    invoice_parser.add_argument("--order", required=True, help="order id, e.g. O-1003")

    subparsers.add_parser("list-orders", help="list all orders on file")

    return parser


def _apply_global_flags(args):
    """Push CLI-level flags into globalstate before any command runs.
    This is the only place outside of orders.py/reports.py/
    order_system.py that touches globalstate directly.
    """
    if getattr(args, "verbose", False):
        globalstate.FLAGS["verbose"] = 1


def dispatch(system, args):
    """Route a parsed command to the matching OrderSystem method.
    Split out from main() so the argument parsing and the dispatch
    logic can be tested (or at least read) independently, even though
    nothing currently imports this function directly.
    """
    if args.command == "report":
        system.cmd_report(args.month)
        return 0
    elif args.command == "invoice":
        system.cmd_invoice(args.order)
        return 0
    elif args.command == "list-orders":
        system.cmd_list_orders()
        return 0
    return 1


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    _apply_global_flags(args)

    system = OrderSystem()
    return dispatch(system, args)


if __name__ == "__main__":
    sys.exit(main())
