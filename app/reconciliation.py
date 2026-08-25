"""Tax reconciliation — an independent recomputation of tax used by the
finance/reporting side to catch drift from the live billing API.

Real-world pattern: Python's built-in round() rounds half-to-even ("banker's
rounding" — round(8.125, 2) == 8.12, not 8.13), which is correct for
statistics but wrong for money: every standard accounting convention rounds
a half-cent up (this is why libraries like `decimal` expose ROUND_HALF_UP
explicitly). billing.compute_tax uses plain round() and inherits Python's
default; this module implements the accounting-correct rounding
independently, so most invoices reconcile cleanly and only the ones whose
subtotal * tax_rate happens to land exactly on a rounding boundary don't.
"""

from __future__ import annotations

import math

from app.currency import to_cents


def round_half_up(value: float) -> float:
    return math.floor(value * 100 + 0.5) / 100


def recompute_tax(subtotal: float, tax_rate: float) -> float:
    return round_half_up(subtotal * tax_rate)


def recompute_refund_adjustment_cents(refund_amount: float) -> int:
    """A refund adjustment on the reconciliation side is also a negative
    dollar figure — the finance team's own recomputation needs it in
    integer cents too, via the same shared to_cents() as billing.py."""
    return to_cents(refund_amount)
