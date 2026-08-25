"""Finalization ledger — records that an invoice has been billed/finalized.

Real-world pattern: this is the classic non-idempotent-retry bug. A client
that times out waiting for /finalize's response has no way to know whether
the request actually succeeded server-side — the only safe client behavior
on a timeout is to retry, and the only safe SERVER behavior is to treat that
retry as a no-op if the first call already went through (this is exactly
why Stripe's charge API requires an Idempotency-Key header on every
request). finalize_invoice() has no such check: every call appends a new
ledger entry unconditionally, so a retried request double-books the same
invoice.
"""

from __future__ import annotations

LEDGER_ENTRIES: list[dict] = []


def finalize_invoice(invoice_id: int, total: float) -> dict:
    entry = {"invoice_id": invoice_id, "total": total}
    LEDGER_ENTRIES.append(entry)  # BUG (P0): unconditional append, no dedup check
    return entry


def ledger_entries_for(invoice_id: int) -> list[dict]:
    return [e for e in LEDGER_ENTRIES if e["invoice_id"] == invoice_id]
