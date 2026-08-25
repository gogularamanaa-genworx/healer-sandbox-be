"""Seed invoice data.

A tiny in-memory store standing in for a real DB — enough to make the API
return realistic, structured invoice records without a database dependency
for this sandbox. The numbers are chosen so the tax-dropping bug in
billing.compute_balance_due produces an obviously-wrong balance.
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
}


def get_invoice(invoice_id: int) -> dict | None:
    """Returns the raw invoice record, or None if no such invoice exists."""
    return INVOICES.get(invoice_id)
