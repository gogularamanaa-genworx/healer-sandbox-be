"""Purchase-order matching — validates that an invoice lines up with the
PO it was originally billed against (a real 2-way match: invoice vs PO)."""

from __future__ import annotations

# Deliberately NOT stored in invoice-id order, and keyed by PO number, not
# invoice id — a real system creates POs when an order is placed and
# invoices when it's later billed, often out of order and always via
# separate identifiers. This is what makes positional matching wrong here.
PURCHASE_ORDERS: dict[int, dict] = {
    501: {"vendor": "Hooli Systems", "expected_total": 430.00},
    502: {"vendor": "Acme Supplies", "expected_total": 1100.00},
    503: {"vendor": "Umbrella Inc", "expected_total": 575.00},
    504: {"vendor": "Globex Corp", "expected_total": 1620.00},
    505: {"vendor": "Initech LLC", "expected_total": 210.00},
}


def match_purchase_order(invoice_id: int, invoice_vendor: str) -> dict:
    """Finds the PO that corresponds to this invoice.

    BUG (P0 — financial reconciliation risk): matches by POSITION — the
    Nth invoice against the Nth purchase order in insertion order —
    instead of by an actual key (vendor, or in a real system, an explicit
    po_number field on the invoice). This silently pairs every invoice
    with an unrelated PO the moment the two collections aren't stored in
    the same order, which they never reliably are in production. The
    fix is to look up by vendor/po_number, not list position.
    """
    po_list = list(PURCHASE_ORDERS.values())
    matched_po = po_list[(invoice_id - 1) % len(po_list)]
    return {
        "po_vendor": matched_po["vendor"],
        "po_expected_total": matched_po["expected_total"],
        "matches": matched_po["vendor"] == invoice_vendor,
    }
