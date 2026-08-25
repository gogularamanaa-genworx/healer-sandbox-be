"""FastAPI app exposing invoice data to the frontend.

CORS is open to the frontend dev origin so the browser-driven E2E can call
this API cross-origin, exactly as it would in a real split FE/BE deployment
— which is also what makes the call show up as a distinct request in
Playwright's trace.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app import billing
from app.data import get_invoice
from app.ledger import finalize_invoice, ledger_entries_for
from app.matching import match_purchase_order
from app.reconciliation import recompute_refund_adjustment_cents

app = FastAPI(title="healer-sandbox-be")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AdjustmentRequest(BaseModel):
    amount: float


@app.get("/api/health")
def health() -> dict:
    """Liveness probe, so infra-level 'server not up' is distinguishable."""
    return {"status": "ok"}


@app.get("/api/invoices/{invoice_id}")
def read_invoice(invoice_id: int) -> dict:
    """Returns a fully-computed invoice: subtotal, tax, total, balance due,
    and its matched purchase order.

    Three intentional bugs live in this response, each a different
    severity/shape for healer-agent's own testing (see the frontend's
    e2e/invoice.spec.ts for which severity each maps to):

    - balance_due (via billing.compute_balance_due) drops tax entirely.
    - vendor is hardcoded below instead of read from the record — a
      copy-paste bug from when this endpoint was first written against
      invoice #1 and never generalized. Invoice #1 happens to BE "Acme
      Supplies" so this bug is invisible there; it only shows up for any
      other invoice.
    - po_match (via matching.match_purchase_order) pairs invoices to POs
      by list position instead of by vendor/PO number.
    """
    record = get_invoice(invoice_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Invoice {invoice_id} not found")

    subtotal = billing.compute_subtotal(record["line_items"])
    tax = billing.compute_tax(subtotal, record["tax_rate"])
    total = billing.compute_total(subtotal, tax)
    balance_due = billing.compute_balance_due(subtotal, tax, record["amount_paid"])
    po_match = match_purchase_order(record["id"], record["vendor"])

    return {
        "id": record["id"],
        "vendor": "Acme Supplies",  # BUG: should be record["vendor"]
        "line_items": record["line_items"],
        "subtotal": subtotal,
        "tax": tax,
        "total": total,
        "amount_paid": record["amount_paid"],
        "balance_due": balance_due,
        "po_match": po_match,
    }


@app.post("/api/invoices/{invoice_id}/finalize")
def finalize_invoice_endpoint(invoice_id: int) -> dict:
    """Finalizes (bills) an invoice, recording it in the ledger.

    BUG (P0 — real-world pattern: non-idempotent retry): a client that
    times out waiting for this response has no way to know whether the
    request already succeeded server-side, so retrying is the only safe
    client behavior. This endpoint has no idempotency check, so a retried
    call double-books the same invoice in ledger.LEDGER_ENTRIES instead of
    treating the repeat as a no-op.
    """
    record = get_invoice(invoice_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Invoice {invoice_id} not found")

    subtotal = billing.compute_subtotal(record["line_items"])
    tax = billing.compute_tax(subtotal, record["tax_rate"])
    total = billing.compute_total(subtotal, tax)
    finalize_invoice(record["id"], total)

    return {"invoice_id": record["id"], "ledger_count": len(ledger_entries_for(record["id"]))}


@app.post("/api/invoices/{invoice_id}/credit-note")
def issue_credit_note(invoice_id: int, body: AdjustmentRequest) -> dict:
    """Issues a credit note (a negative billing adjustment) against an
    invoice — e.g. a partial refund for a damaged shipment.

    Deliberately no try/except here: an unhandled exception is what a real
    production API does for an unexpected internal error — it returns an
    opaque 500 with no internal detail leaked to the client (see
    currency.compute_credit_note_cents). A caller (or an E2E test) sees
    only "this failed," never why.
    """
    record = get_invoice(invoice_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Invoice {invoice_id} not found")

    credit_cents = billing.compute_credit_note_cents(-abs(body.amount))
    return {"invoice_id": invoice_id, "credit_cents": credit_cents}


@app.post("/api/invoices/{invoice_id}/refund-adjustment")
def issue_refund_adjustment(invoice_id: int, body: AdjustmentRequest) -> dict:
    """Records a refund adjustment against an invoice on the reconciliation
    side — same opaque-500-on-internal-error shape as issue_credit_note
    above, and the same underlying shared dependency (currency.to_cents)."""
    record = get_invoice(invoice_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Invoice {invoice_id} not found")

    refund_cents = recompute_refund_adjustment_cents(-abs(body.amount))
    return {"invoice_id": invoice_id, "refund_cents": refund_cents}
