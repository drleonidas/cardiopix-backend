"""Business intelligence helpers for exam insights."""
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from typing import Iterable, List

from .exam import ExamRecord


@dataclass(frozen=True)
class MonthlySummary:
    month: date
    total_exams: int
    revenue: float

    @property
    def label(self) -> str:
        return self.month.strftime("%Y-%m")


@dataclass(frozen=True)
class DashboardData:
    exams_per_month: List[MonthlySummary]
    revenue_per_month: List[MonthlySummary]


def summarize_exams(exams: Iterable[ExamRecord]) -> DashboardData:
    """Aggregate exam volume and revenue for dashboard visualizations."""

    volume_bucket: defaultdict[str, int] = defaultdict(int)
    revenue_bucket: defaultdict[str, float] = defaultdict(float)

    for exam in exams:
        label = exam.performed_at.strftime("%Y-%m")
        volume_bucket[label] += 1
        revenue_bucket[label] += float(exam.price)

    summaries = _build_monthly_summaries(volume_bucket, revenue_bucket)

    return DashboardData(
        exams_per_month=summaries,
        revenue_per_month=summaries,
    )


def _build_monthly_summaries(volume_bucket: dict[str, int], revenue_bucket: dict[str, float]) -> List[MonthlySummary]:
    months = sorted(volume_bucket.keys())
    summaries: List[MonthlySummary] = []

    for month in months:
        year, month_number = map(int, month.split("-"))
        month_date = date(year, month_number, 1)
        summaries.append(
            MonthlySummary(
                month=month_date,
                total_exams=volume_bucket[month],
                revenue=round(revenue_bucket[month], 2),
            )
        )

    return summaries
