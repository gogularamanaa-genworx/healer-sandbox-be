"""Vendor notification — emails the vendor when an invoice is finalized.

Two deliberately DIFFERENT failure shapes here, on purpose — they should
be classified differently by healer-agent, not treated the same:

- send_invoice_notification: a real (here, unreachable) network call to an
  email microservice. Nothing listens on this port in this sandbox or in
  CI, so this raises a genuine connection error — an INFRA failure, not a
  code defect. The service being down is an environment problem; there is
  nothing to "fix" in this function.
- build_notification_payload: a real code defect (accesses a field the
  invoice record never has). This is an APP-BUG — the service being up or
  down is irrelevant, the payload construction itself is broken.
"""

from __future__ import annotations

import httpx

# Deliberately unreachable — simulates hitting a real internal
# microservice that happens to be down, not synthesized failure text.
EMAIL_SERVICE_URL = "http://localhost:9999/send"


def send_invoice_notification(invoice: dict) -> None:
    """POSTs the invoice to the (here, unreachable) email microservice."""
    httpx.post(EMAIL_SERVICE_URL, json=invoice, timeout=2.0)


def build_notification_payload(invoice: dict) -> dict:
    """Builds the payload sent to the email microservice.

    BUG (app-bug, not infra): assumes every invoice record has a
    'contact_email' field. The seed data never sets one, so this raises a
    KeyError for every invoice — a real code defect, unrelated to whether
    the email service is reachable.
    """
    return {
        "to": invoice["contact_email"],
        "subject": f"Invoice #{invoice['id']} from {invoice['vendor']}",
        "total": invoice["total"],
    }
