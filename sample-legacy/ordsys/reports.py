"""Report and invoice text formatting helpers for ORDSYS/85.

The actual report assembly (which orders go where, how totals are
computed) lives in order_system.py. This module only holds the low
level text layout pieces that are shared between the report, invoice,
and order list output.
"""

from ordsys import globalstate

LINE = "=" * 80
THIN_LINE = "-" * 80


def report_header(title):
    """Build a boxed header line for a report. Also flips the system
    into strict mode for the duration of report generation - this has
    always been done here, nobody remembers exactly why.
    """
    globalstate.FLAGS["strict_mode"] = 1
    return "\n".join([LINE, title, LINE])


def report_footer():
    globalstate.FLAGS["strict_mode"] = 0
    return LINE


def format_row(columns):
    """Join a list of (text, width, align) tuples into a single
    fixed-width text row. align is 'l' or 'r'. Columns are separated
    by a two-space gutter so right-aligned numeric columns do not run
    into the next column's text.
    """
    parts = []
    for text, width, align in columns:
        text = str(text)
        if align == "r":
            cell = text.rjust(width)
        else:
            cell = text.ljust(width)
        parts.append(cell)
    return "  ".join(parts).rstrip()


def format_label_value(label, value, width=80):
    label_col = label.ljust(15)
    return "%s%s" % (label_col, value)


DOUBLE_LINE = "=" * 80
DASH_LINE = "-" * 40


def format_row_v1(columns, widths):
    """Original (pre-gutter) row formatter. Superseded by format_row()
    above once right-aligned numeric columns started running into the
    following left-aligned column with no visible gap. Kept for
    reference and because a couple of archived report snapshots were
    generated with this exact (misaligned) layout and are still
    compared against by hand occasionally.
    """
    parts = []
    for text, width in zip(columns, widths):
        parts.append(str(text).ljust(width))
    return "".join(parts)


def format_currency_column(value, width):
    """Right-align a pre-formatted currency string within a fixed
    width. Thin wrapper kept around for symmetry with format_row();
    most callers use format_row() directly instead.
    """
    return str(value).rjust(width)


def format_percent_row(label, rate, width=58):
    """Format a label/percentage pair the same way discount and tax
    lines are formatted, for verbose/debug output. Not used by the
    standard report or invoice commands.
    """
    return format_row([(label, width, "l"), (util_format_percent(rate), 18, "r")])


def util_format_percent(rate):
    # Small local copy to avoid an extra import for one call site;
    # see util.format_percent for the canonical version.
    return "%.1f%%" % (rate * 100.0)
