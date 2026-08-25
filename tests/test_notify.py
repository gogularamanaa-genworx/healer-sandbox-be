from app.notify import build_notification_payload, send_invoice_notification


def test_p1_vendor_notification_is_sent_on_invoice_finalization():
    # NOT a code bug — the email microservice itself is unreachable (see
    # notify.py's EMAIL_SERVICE_URL). This should classify as INFRA, not
    # app-bug: there is no code fix available here, the service is down.
    invoice = {"id": 1, "vendor": "Acme Supplies", "total": 1100.00}
    send_invoice_notification(invoice)


def test_p1_notification_payload_includes_contact_email():
    # NOT an infra issue — the email service being up or down is
    # irrelevant here. This is a genuine code defect: invoice records
    # never carry a contact_email field, so building the payload
    # KeyErrors before any network call is even attempted.
    invoice = {"id": 1, "vendor": "Acme Supplies", "total": 1100.00}
    payload = build_notification_payload(invoice)
    assert payload["to"]
