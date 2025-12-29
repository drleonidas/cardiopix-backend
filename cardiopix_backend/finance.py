"""Financial split logic for CardioPix payments."""
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP, getcontext
from typing import Dict

getcontext().prec = 28


@dataclass(frozen=True)
class PaymentSplit:
    """Represents a payment split calculation."""

    gross_amount: Decimal
    processing_fees: Decimal
    taxes_2026: Decimal
    doctor_payout: Decimal

    @property
    def net_profit(self) -> Decimal:
        """Compute the liquid profit after deductions.

        The formula is: Gross - Taxas - Impostos 2026 - Repasse Médico.
        Values are rounded to two decimal places using bankers' rounding.
        """

        net = self.gross_amount - self.processing_fees - self.taxes_2026 - self.doctor_payout
        return _quantize_currency(net)

    def breakdown(self) -> Dict[str, Decimal]:
        """Return a detailed breakdown of the split values."""

        return {
            "gross_amount": _quantize_currency(self.gross_amount),
            "processing_fees": _quantize_currency(self.processing_fees),
            "taxes_2026": _quantize_currency(self.taxes_2026),
            "doctor_payout": _quantize_currency(self.doctor_payout),
            "net_profit": self.net_profit,
        }


def build_payment_split(
    gross_amount: float | Decimal,
    processing_fees: float | Decimal,
    taxes_2026: float | Decimal,
    doctor_payout: float | Decimal,
) -> PaymentSplit:
    """Create a :class:`PaymentSplit` ensuring all inputs are valid.

    Args:
        gross_amount: Valor bruto recebido.
        processing_fees: Taxas aplicadas ao pagamento.
        taxes_2026: Impostos previstos para 2026.
        doctor_payout: Repasse devido ao médico responsável.

    Raises:
        ValueError: If any value is negative or if deductions exceed gross.
    """

    amounts = {
        "gross_amount": gross_amount,
        "processing_fees": processing_fees,
        "taxes_2026": taxes_2026,
        "doctor_payout": doctor_payout,
    }

    decimals = {name: _to_decimal(value, name) for name, value in amounts.items()}

    _validate_non_negative(decimals)
    _validate_not_exceeding_gross(decimals)

    return PaymentSplit(**decimals)


def _validate_non_negative(values: Dict[str, Decimal]) -> None:
    negatives = [name for name, value in values.items() if value < 0]
    if negatives:
        raise ValueError(f"Valores não podem ser negativos: {', '.join(sorted(negatives))}")


def _validate_not_exceeding_gross(values: Dict[str, Decimal]) -> None:
    deductions = values["processing_fees"] + values["taxes_2026"] + values["doctor_payout"]
    if deductions > values["gross_amount"]:
        raise ValueError("Deduções não podem ultrapassar o valor bruto")


def _quantize_currency(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _to_decimal(value: float | Decimal, name: str) -> Decimal:
    try:
        decimal_value = Decimal(str(value))
    except Exception as exc:  # pragma: no cover - defensive
        raise ValueError(f"Valor inválido para {name}: {value}") from exc
    return _quantize_currency(decimal_value)
