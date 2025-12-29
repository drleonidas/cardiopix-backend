from decimal import Decimal

import pytest

from cardiopix_backend.finance import build_payment_split


def test_build_payment_split_returns_breakdown():
    split = build_payment_split(1000, 50.75, 120.40, 300)

    assert split.net_profit == Decimal("528.85")
    breakdown = split.breakdown()
    assert breakdown == {
        "gross_amount": Decimal("1000.00"),
        "processing_fees": Decimal("50.75"),
        "taxes_2026": Decimal("120.40"),
        "doctor_payout": Decimal("300.00"),
        "net_profit": Decimal("528.85"),
    }


def test_build_payment_split_validates_negative_inputs():
    with pytest.raises(ValueError):
        build_payment_split(-1, 0, 0, 0)


def test_build_payment_split_validates_deductions_not_exceeding_gross():
    with pytest.raises(ValueError):
        build_payment_split(100, 40, 40, 30)
