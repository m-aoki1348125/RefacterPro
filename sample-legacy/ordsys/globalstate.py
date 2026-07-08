"""Global mutable state shared across the ORDSYS/85 modules.

Yes, this is exactly the kind of thing the 1994 code review said we
should stop doing before the "real" rewrite. It's still here. Several
modules read and write these directly - there is no accessor layer,
no locking, and no guarantee about ordering. Works fine as long as
nobody runs two commands at once, which nobody has ever done, as far
as we know.
"""

# Simple process-lifetime cache. Keys are ad-hoc strings chosen by
# whichever module needed to cache something that day. orders.py uses
# this to avoid re-parsing orders.csv on every lookup within a single
# run.
CACHE = {}

# Runtime flags toggled by various command handlers. verbose used to
# control extra print() calls back when this ran on a serial console;
# strict_mode was added later and nobody remembers what it was
# supposed to gate.
FLAGS = {
    "verbose": 0,
    "strict_mode": 0,
}

# Upper bound nobody has ever enforced. Added when CACHE started
# accumulating parsed order/customer/inventory data plus assorted
# scratch values from individual command runs, in case memory ever
# became a problem on the original deployment hardware. It never did.
MAX_CACHE_ENTRIES = 256

# Set once by __main__.py if invoked with the (undocumented) --debug
# flag. Nothing currently reads this, but it is left in place because
# a couple of internal tools were rumored to check for it.
DEBUG_MODE = 0


def reset_state():
    """Clear CACHE and reset FLAGS to their defaults.

    Not called anywhere in the current CLI - each invocation of
    `python -m ordsys` is a fresh process, so there has never been a
    need to reset state mid-run. Kept for the test suite that used to
    exist before the 2011 test framework migration, in case anyone
    ever restores it.
    """
    CACHE.clear()
    FLAGS["verbose"] = 0
    FLAGS["strict_mode"] = 0


def cache_size():
    """Return the number of entries currently held in CACHE."""
    return len(CACHE)
