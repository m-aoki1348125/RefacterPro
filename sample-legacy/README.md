# ORDSYS/85

Order and invoice management system, originally written for in-house
minicomputer hardware in 1985. Ported to Python 3 in the mid-2010s as
a stopgap while a full rewrite was being scoped. The rewrite never
happened; this is the stopgap's stopgap, and it is still what runs
month-end reporting today.

ORDSYS/85 has no external dependencies - it runs on the Python 3
standard library only, the same way it has since the port.

## Requirements

- Python 3 (standard library only, no third-party packages)

## Usage

Run all commands from the `sample-legacy/` directory so the `data/`
folder can be found:

```
python -m ordsys report --month 1986-06
python -m ordsys invoice --order O-1003
python -m ordsys list-orders
```

### `report --month YYYY-MM`

Prints the monthly sales report: every order placed in the given
month, the customer it was billed to, and the final billed amount,
followed by order count and total.

### `invoice --order ORDER-ID`

Prints a single-order invoice showing the line item, subtotal,
discount, tax, and total for one order.

### `list-orders`

Prints every order on file with its customer, date, SKU, quantity,
and customer account type.

## Data files

All data lives under `data/`:

- `orders.csv` - order records (CSV)
- `customers.json` - customer accounts (JSON)
- `inventory.csv` - inventory / price list (CSV)
- `config.ini` - system configuration

## Layout

```
ordsys/
    __main__.py       CLI entry point
    order_system.py   core order processing engine
    orders.py          order lookups
    customers.py        customer lookups
    inventory.py        inventory lookups
    pricing.py           line pricing calculations
    tax.py               sales tax schedule
    discounts.py         customer discount rules
    reports.py            report/invoice text formatting
    storage.py            file I/O for orders/customers/inventory
    legacy_compat.py      compatibility shims from earlier ports
    globalstate.py        shared runtime state
    util.py               general helpers
tests/
    test_orders_old.py    regression tests
data/
    orders.csv, customers.json, inventory.csv, config.ini
```

## Development notes

Account types are `GOLD`, `STANDARD`, and `WHOLESALE`; pricing and
discount rules differ by type. Sales tax is calculated from the order
date according to the schedule in `tax.py`. Final invoice and report
totals are rounded using whichever handler is configured in
`data/config.ini`.

Run the test suite with:

```
python -m unittest discover -s tests -v
```
