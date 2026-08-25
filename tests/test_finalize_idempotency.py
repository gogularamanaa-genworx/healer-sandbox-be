"""Finalize-endpoint idempotency check.

Real-world pattern: a client that times out waiting for /finalize's
response has no way to know if the request actually succeeded server-side
— retrying is the only safe thing it can do, and a correct API must treat
that retry as a no-op if the first call already went through (this is
exactly why Stripe's charge API requires an Idempotency-Key header). This
test simulates that retry directly against the real endpoint.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_p0_retried_finalize_does_not_double_book_the_ledger():
    invoice_id = 2
    first = client.post(f"/api/invoices/{invoice_id}/finalize")
    assert first.status_code == 200

    retry = client.post(f"/api/invoices/{invoice_id}/finalize")
    assert retry.status_code == 200
    assert retry.json()["ledger_count"] == 1
