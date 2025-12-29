"""Exportação e ordenação de rankings de produtividade."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from .aggregator import DoctorProductivity, rank_productivity


def export_ranking(
    metrics: Iterable[DoctorProductivity],
    *,
    order_by: str = "concluded_reports",
    descending: bool = True,
    destination: str | Path = "productivity_ranking.csv",
) -> Path:
    """Ordena e exporta o ranking para CSV.

    Args:
        metrics: Lista de métricas por médico.
        order_by: Campo de ordenação usado para o ranking.
        descending: Direção da ordenação.
        destination: Caminho do arquivo CSV gerado.

    Returns:
        Caminho para o arquivo exportado.
    """

    ordered = rank_productivity(list(metrics), order_by=order_by, descending=descending)
    destination_path = Path(destination)

    fieldnames = [
        "doctor_id",
        "concluded_reports",
        "total_value",
        "average_ticket",
        "payable_total",
    ]

    with destination_path.open("w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for metric in ordered:
            writer.writerow({
                "doctor_id": metric.doctor_id,
                "concluded_reports": metric.concluded_reports,
                "total_value": f"{metric.total_value:.2f}",
                "average_ticket": f"{metric.average_ticket:.2f}",
                "payable_total": f"{metric.payable_total:.2f}",
            })

    return destination_path
