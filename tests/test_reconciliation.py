"""Reconciliation check: the live billing API's tax figure should match an
independent recomputation using standard (round-half-up) rounding.

Real-world pattern: this is exactly the kind of discrepancy a finance
team's reconciliation report catches. Most invoices reconcile cleanly —
only the ones whose subtotal * tax_rate lands exactly on a rounding
boundary reveal that billing.compute_tax's plain round() (banker's
rounding) disagrees with the accounting-standard round-half-up.
"""

from app import billing
from app.data import INVOICES
from app.reconciliation import recompute_refund_adjustment_cents, recompute_tax


def _tax_reconciles(invoice_id: int) -> bool:
    record = INVOICES[invoice_id]
    subtotal = billing.compute_subtotal(record["line_items"])
    live_tax = billing.compute_tax(subtotal, record["tax_rate"])
    reconciled_tax = recompute_tax(subtotal, record["tax_rate"])
    return live_tax == reconciled_tax


def test_invoice_1_tax_reconciles():
    assert _tax_reconciles(1)


def test_invoice_2_tax_reconciles():
    assert _tax_reconciles(2)


def test_invoice_3_tax_reconciles():
    assert _tax_reconciles(3)


def test_invoice_4_tax_reconciles():
    assert _tax_reconciles(4)


def test_invoice_5_tax_reconciles():
    assert _tax_reconciles(5)


def test_p1_invoice_6_tax_reconciles_with_standard_rounding():
    # Invoice 6's subtotal ($162.50) * tax_rate (0.05) = 8.125 exactly —
    # a rounding boundary where round() and round-half-up diverge
    # (8.12 vs 8.13). Every other invoice above lands clear of any such
    # boundary and reconciles fine, which is the point: this isn't a
    # systemic bug that breaks every invoice, it's the subtle kind that
    # only shows up for specific fractional-cent amounts.
    assert _tax_reconciles(6)


def test_p1_refund_adjustment_converts_to_cents():
    # A refund adjustment on the reconciliation side is also a negative
    # dollar figure — e.g. a $25 refund shows up here as -25.00.
    assert recompute_refund_adjustment_cents(-25.00) == -2500
