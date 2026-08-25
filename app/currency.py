"""Shared money utility: converts a dollar amount to integer cents — the
standard way financial code avoids float rounding drift (see
reconciliation.py's own docstring on why raw floats are risky for money).
Used by both billing (credit notes) and reconciliation (refund
adjustments) wherever an amount needs to move to/from cents.

Real-world pattern: a shared, low-level utility used by several otherwise-
unrelated features means a bug here doesn't fail in isolation — it cascades
into every feature that depends on it, each looking like an unrelated
failure in a different module until you notice they all pass through this
one file.
"""

from __future__ import annotations


def to_cents(amount: float) -> int:
    # BUG: this assert held for to_cents()'s FIRST caller (regular invoice
    # totals, always >= 0) but was never revisited when a second caller
    # showed up needing a negative amount — a credit note or refund
    # adjustment is a perfectly legitimate negative dollar figure. Because
    # to_cents() is shared, every feature that legitimately needs to
    # convert one fails here, not in its own code.
    assert amount >= 0, "to_cents() only accepts non-negative amounts"
    return round(amount * 100)
