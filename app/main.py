"""FastAPI app exposing invoice data to the frontend.

CORS is open to the frontend dev origin so the browser-driven E2E can call
this API cross-origin, exactly as it would in a real split FE/BE deployment
— which is also what makes the call show up as a distinct request in
Playwright's trace.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app import billing
from app.data import get_invoice

app = FastAPI(title="healer-sandbox-be")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict:
    """Liveness probe, so infra-level 'server not up' is distinguishable."""
    return {"status": "ok"}


@app.get("/api/invoices/{invoice_id}")
def read_invoice(invoice_id: int) -> dict:
    """Returns a fully-computed invoice: subtotal, tax, total, balance due.

    The balance_due field is computed by billing.compute_balance_due, which
    carries the intentional tax-dropping bug — so this endpoint returns a
    200 with numerically wrong data, not an error.
    """
    record = get_invoice(invoice_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Invoice {invoice_id} not found")

    subtotal = billing.compute_subtotal(record["line_items"])
    tax = billing.compute_tax(subtotal, record["tax_rate"])
    total = billing.compute_total(subtotal, tax)
    balance_due = billing.compute_balance_due(subtotal, tax, record["amount_paid"])

    return {
        "id": record["id"],
        "vendor": record["vendor"],
        "line_items": record["line_items"],
        "subtotal": subtotal,
        "tax": tax,
        "total": total,
        "amount_paid": record["amount_paid"],
        "balance_due": balance_due,
    }
