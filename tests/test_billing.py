"""Backend unit tests for billing math.

Deliberately realistic coverage GAP: subtotal, tax, and total are each
tested and pass — but there is no test for compute_balance_due, which is
exactly how the tax-dropping bug ships to production green. The defect only
surfaces downstream, in the frontend E2E that renders the wrong balance.
This mirrors real life: the integration-level money field is the one nobody
wrote a unit test for.
"""

from app import billing


def test_subtotal_sums_line_items():
    items = [
        {"description": "Widget", "quantity": 10, "unit_price": 50.0},
        {"description": "Gadget", "quantity": 5, "unit_price": 100.0},
    ]
    assert billing.compute_subtotal(items) == 1000.0


def test_tax_at_ten_percent():
    assert billing.compute_tax(1000.0, 0.10) == 100.0


def test_total_is_subtotal_plus_tax():
    assert billing.compute_total(1000.0, 100.0) == 1100.0
