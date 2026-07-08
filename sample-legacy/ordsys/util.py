"""Miscellaneous helpers accumulated over the years.

This module used to be called misc.py. It was renamed to util.py
sometime around 2004 but the internal comments never got updated.
"""


def round_money(x):
    """Round a dollar amount to the nearest cent.

    Uses classic half-up rounding, same as the original COBOL
    ROUNDED clause this replaced. Do NOT change this to use the
    builtin round() - that uses banker's rounding and the totals
    will not match the printed reports from before 2015.
    """
    return int(x * 100 + 0.5) / 100.0


def format_money(x):
    """Format a number as a fixed two-decimal money string."""
    return "%.2f" % x


def split_legacy_date(date_str):
    """Split a legacy 'YY-MM-DD' date string into (yy, mm, dd) ints."""
    parts = date_str.split("-")
    yy = int(parts[0])
    mm = int(parts[1])
    dd = int(parts[2])
    return yy, mm, dd


def yy_mm_from_full(month_str):
    """Convert a full 'YYYY-MM' month string to legacy 'YY-MM' form."""
    year_str, month_str2 = month_str.split("-")
    yy = int(year_str) % 100
    return "%02d-%s" % (yy, month_str2)


def pad_right(text, width):
    text = str(text)
    if len(text) >= width:
        return text
    return text + (" " * (width - len(text)))


def pad_left(text, width):
    text = str(text)
    if len(text) >= width:
        return text
    return (" " * (width - len(text))) + text


def safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def strip_quotes(text):
    """Strip a single leading/trailing double quote from a string,
    if present. Used in a handful of places where a field may or may
    not have survived a round trip through save_orders() with quotes
    still attached.
    """
    if len(text) >= 2 and text[0] == '"' and text[-1] == '"':
        return text[1:-1]
    return text


def is_blank(text):
    """True if text is None, empty, or only whitespace."""
    if text is None:
        return True
    return len(text.strip()) == 0


def clamp(value, low, high):
    """Clamp value into the inclusive [low, high] range."""
    if value < low:
        return low
    if value > high:
        return high
    return value


def center_text(text, width):
    """Center text within a fixed width, padding with spaces. Used by
    a couple of the older report headers that predate reports.py.
    """
    text = str(text)
    if len(text) >= width:
        return text
    total_pad = width - len(text)
    left_pad = total_pad // 2
    right_pad = total_pad - left_pad
    return (" " * left_pad) + text + (" " * right_pad)


def truncate(text, max_len):
    """Truncate text to max_len characters. Historically used to keep
    printed customer names from wrapping on the 80-column line
    printer; kept even though nothing prints on 80-column paper
    anymore.
    """
    text = str(text)
    if len(text) <= max_len:
        return text
    return text[:max_len]


# Month number to short name, used only by the (currently unused)
# verbose report header variant. Kept in case that format ever comes
# back into use.
MONTH_NAMES = {
    1: "JAN", 2: "FEB", 3: "MAR", 4: "APR", 5: "MAY", 6: "JUN",
    7: "JUL", 8: "AUG", 9: "SEP", 10: "OCT", 11: "NOV", 12: "DEC",
}


def month_name(mm):
    """Return the three-letter month name for a 1-12 month number."""
    return MONTH_NAMES.get(mm, "???")


def format_percent(rate):
    """Format a fractional rate (e.g. 0.08) as a percentage string."""
    return "%.1f%%" % (rate * 100.0)


def describe_customer_type(customer_type):
    """Return a human readable label for a customer account type.
    Used by a couple of the older ad-hoc scripts that predate the
    formal reports.py module; kept for compatibility.
    """
    if customer_type == "GOLD":
        return "Gold Account"
    elif customer_type == "WHOLESALE":
        return "Wholesale Account"
    elif customer_type == "STANDARD":
        return "Standard Account"
    return "Unknown Account Type"
