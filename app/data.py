"""Seed invoice data.

A tiny in-memory store standing in for a real DB — enough to make the API
return realistic, structured invoice records without a database dependency
for this sandbox. Five invoices, deliberately, not one: both bugs in
main.py (dropped tax, hardcoded vendor) are systemic — they apply to
EVERY invoice this store returns, not a single unlucky one — so the
number of invoices here directly controls how many correlated failures
the P0/P1 scenario produces. This is the difference between "one invoice
is wrong" (a bug to schedule) and "no invoice in the system can be billed
correctly" (a P0 that blocks production).
"""

from __future__ import annotations

INVOICES: dict[int, dict] = {
    1: {
        "id": 1,
        "vendor": "Acme Supplies",
        "tax_rate": 0.10,
        "amount_paid": 400.00,
        "line_items": [
            {"description": "Widget", "quantity": 10, "unit_price": 50.00},
            {"description": "Gadget", "quantity": 5, "unit_price": 100.00},
        ],
    },
    2: {
        "id": 2,
        "vendor": "Globex Corp",
        "tax_rate": 0.08,
        "amount_paid": 200.00,
        "line_items": [
            {"description": "Consulting hours", "quantity": 20, "unit_price": 75.00},
        ],
    },
    3: {
        "id": 3,
        "vendor": "Initech LLC",
        "tax_rate": 0.05,
        "amount_paid": 50.00,
        "line_items": [
            {"description": "Software license", "quantity": 10, "unit_price": 20.00},
        ],
    },
    4: {
        "id": 4,
        "vendor": "Umbrella Inc",
        "tax_rate": 0.15,
        "amount_paid": 75.00,
        "line_items": [
            {"description": "Lab equipment", "quantity": 4, "unit_price": 125.00},
        ],
    },
    5: {
        "id": 5,
        "vendor": "Hooli Systems",
        "tax_rate": 0.075,
        "amount_paid": 130.00,
        "line_items": [
            {"description": "Cloud hosting", "quantity": 8, "unit_price": 50.00},
        ],
    },
}


def get_invoice(invoice_id: int) -> dict | None:
    """Returns the raw invoice record, or None if no such invoice exists."""
    return INVOICES.get(invoice_id)
