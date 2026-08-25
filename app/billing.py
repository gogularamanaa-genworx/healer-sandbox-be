"""Invoice billing calculations.

This is the module that owns the money math for an invoice. The bug that the
cross-repo E2E scenario is designed to catch lives here — see
compute_balance_due.
"""

from __future__ import annotations


def compute_subtotal(line_items: list[dict]) -> float:
    """Sum of quantity * unit_price across all line items."""
    return sum(item["quantity"] * item["unit_price"] for item in line_items)


def compute_tax(subtotal: float, tax_rate: float) -> float:
    """Tax on the subtotal at the given rate."""
    return round(subtotal * tax_rate, 2)


def compute_total(subtotal: float, tax: float) -> float:
    """Grand total = subtotal + tax (before any payments)."""
    return round(subtotal + tax, 2)


def compute_balance_due(subtotal: float, tax: float, amount_paid: float) -> float:
    """Balance still owed after payments.

    BUG (intentional, P0 financial defect): the balance is computed off the
    pre-tax subtotal instead of the tax-inclusive total, so tax is silently
    dropped from what the customer is asked to pay. The correct formula is
    (subtotal + tax) - amount_paid; this returns subtotal - amount_paid.

    A $1000 invoice with $100 tax and a $400 payment should show $700 due;
    this returns $600 — the customer is under-billed by exactly the tax.
    """
    return round(subtotal - amount_paid, 2)
