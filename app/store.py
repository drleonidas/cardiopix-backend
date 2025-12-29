from typing import Dict, Iterable

from .models import Report, ReportStatus


class InMemoryReportStore:
    def __init__(self) -> None:
        self._reports: Dict[str, Report] = {}

    def seed(self, reports: Iterable[Report]) -> None:
        for report in reports:
            self._reports[report.id] = report

    def list_reports(self) -> list[Report]:
        return list(self._reports.values())

    def get(self, report_id: str) -> Report:
        report = self._reports.get(report_id)
        if not report:
            raise KeyError(f"Report {report_id} not found")
        return report

    def mark_lauded(self, report_id: str) -> Report:
        report = self.get(report_id)
        if report.status == ReportStatus.LAUDED:
            return report
        report.mark_lauded()
        self._reports[report_id] = report
        return report
