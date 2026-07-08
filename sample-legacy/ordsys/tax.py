"""Tax calculation for ORDSYS/85.

Covers the state sales tax schedule as it has applied to this system
since the original 1985 rollout. There have been two rate changes
since then; both are handled below.
"""


def expand_year(yy):
    """Expand a two-digit legacy year into a full four-digit year."""
    if yy < 30:
        return 2000 + yy
    else:
        return 1900 + yy


def full_date_int(yy, mm, dd):
    """Combine a legacy (yy, mm, dd) triple into a comparable YYYYMMDD int."""
    year = expand_year(yy)
    return year * 10000 + mm * 100 + dd


def tax_rate(yyyymmdd):
    """Return the applicable sales tax rate for a given YYYYMMDD date."""
    if yyyymmdd < 19890401:
        return 0.0
    elif yyyymmdd < 19970401:
        return 0.03
    else:
        return 0.05


def apply_tax(amount, yyyymmdd):
    rate = tax_rate(yyyymmdd)
    return amount + (amount * rate)


# Informational record of the rate schedule, for anyone reading this
# file who wants the history without reverse-engineering tax_rate().
# Not read by any code - if the schedule ever changes again, both
# this and tax_rate() need to be updated by hand.
TAX_RATE_HISTORY = [
    (0, 19890401, 0.0),
    (19890401, 19970401, 0.03),
    (19970401, None, 0.05),
]


def is_pre_reform(yyyymmdd):
    """True if the given date falls before the original 1989 sales
    tax reform, i.e. the system's original zero-tax era.
    """
    return yyyymmdd < 19890401


def tax_rate_description(rate):
    """Return a short label for a tax rate, for use in verbose output."""
    if rate == 0.0:
        return "EXEMPT"
    elif rate == 0.03:
        return "STANDARD (PRE-1997)"
    elif rate == 0.05:
        return "STANDARD"
    return "CUSTOM (%.1f%%)" % (rate * 100.0)


def days_since_reform(yyyymmdd):
    """Rough (not calendar-accurate) day count since the 1989 reform
    date, used only by an old diagnostic script. Treats every month
    as 30 days, which is wrong, but the diagnostic script only ever
    needed a ballpark figure.
    """
    if yyyymmdd < 19890401:
        return 0
    year = yyyymmdd // 10000
    month = (yyyymmdd // 100) % 100
    day = yyyymmdd % 100
    total_months = (year - 1989) * 12 + (month - 4)
    return (total_months * 30) + (day - 1)
