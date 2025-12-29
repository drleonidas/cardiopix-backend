"""Ferramentas para calcular produtividade de médicos a partir de laudos."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, Iterable, List, Optional, Sequence


@dataclass
class PaymentPolicy:
    """Regras para calcular valores vinculados à política de pagamentos.

    Attributes:
        percentage: Percentual aplicado sobre o valor bruto dos laudos concluídos.
        fixed_bonus: Valor fixo acrescido por laudo concluído.
    """

    percentage: float = 0.0
    fixed_bonus: float = 0.0


@dataclass
class DoctorProductivity:
    """Métricas agregadas de produtividade por médico."""

    doctor_id: str
    concluded_reports: int
    total_value: float
    average_ticket: float
    payable_total: float


def _coerce_date(value: date | datetime | str) -> date:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        return datetime.fromisoformat(value).date()
    raise TypeError("start_date/end_date devem ser date, datetime ou string ISO.")


def _apply_payment_policy(total_value: float, concluded: int, policy: Optional[PaymentPolicy]) -> float:
    if policy is None:
        return total_value
    return total_value * (1 + policy.percentage) + policy.fixed_bonus * concluded


def aggregate_by_doctor(
    reports: Iterable[Dict],
    start_date: date | datetime | str,
    end_date: date | datetime | str,
    *,
    payment_policy: Optional[PaymentPolicy] = None,
    concluded_statuses: Sequence[str] = ("concluido", "concluído", "concluded", "completed"),
) -> List[DoctorProductivity]:
    """Agrupa laudos concluídos por médico no período especificado.

    Args:
        reports: Iterable com dicionários contendo ``doctor_id``, ``status``, ``value`` e ``created_at``.
        start_date: Início do intervalo (date, datetime ou string ISO).
        end_date: Fim do intervalo (date, datetime ou string ISO).
        payment_policy: Política aplicada para calcular o valor a pagar.
        concluded_statuses: Lista de status que representam laudos concluídos.

    Returns:
        Lista de :class:`DoctorProductivity` para cada médico encontrado.
    """

    start = _coerce_date(start_date)
    end = _coerce_date(end_date)

    productivity: Dict[str, Dict[str, float]] = {}

    for report in reports:
        doctor = str(report.get("doctor_id"))
        status = str(report.get("status", "")).lower()
        created_at = report.get("created_at")
        value = float(report.get("value", 0))

        if not doctor or not created_at:
            continue

        created = _coerce_date(created_at)
        if created < start or created > end:
            continue

        if status not in [s.lower() for s in concluded_statuses]:
            continue

        if doctor not in productivity:
            productivity[doctor] = {"count": 0, "total": 0.0}

        productivity[doctor]["count"] += 1
        productivity[doctor]["total"] += value

    results: List[DoctorProductivity] = []
    for doctor, data in productivity.items():
        concluded = int(data["count"])
        total_value = float(data["total"])
        average_ticket = total_value / concluded if concluded else 0.0
        payable_total = _apply_payment_policy(total_value, concluded, payment_policy)
        results.append(
            DoctorProductivity(
                doctor_id=doctor,
                concluded_reports=concluded,
                total_value=total_value,
                average_ticket=average_ticket,
                payable_total=payable_total,
            )
        )

    return results


def rank_productivity(
    metrics: List[DoctorProductivity],
    *,
    order_by: str = "concluded_reports",
    descending: bool = True,
) -> List[DoctorProductivity]:
    """Ordena a lista de produtividade utilizando o campo escolhido."""

    allowed = {"doctor_id", "concluded_reports", "total_value", "average_ticket", "payable_total"}
    if order_by not in allowed:
        raise ValueError(f"order_by deve ser um dos {sorted(allowed)}")

    return sorted(metrics, key=lambda m: getattr(m, order_by), reverse=descending)
