from datetime import datetime

from cardiopix_backend.dashboard import summarize_exams
from cardiopix_backend.exam import Contact, ExamRecord, ExamStatus


def test_summarize_exams_groups_by_month():
    exams = [
        ExamRecord("EX1", datetime(2026, 1, 10), 150.0, ExamStatus.LAUDADO, Contact("Ana")),
        ExamRecord("EX2", datetime(2026, 1, 20), 200.0, ExamStatus.LAUDADO, Contact("Ana")),
        ExamRecord("EX3", datetime(2026, 2, 5), 300.0, ExamStatus.LAUDADO, Contact("Bruno")),
    ]

    dashboard = summarize_exams(exams)

    assert [item.label for item in dashboard.exams_per_month] == ["2026-01", "2026-02"]
    january, february = dashboard.revenue_per_month
    assert january.total_exams == 2
    assert january.revenue == 350.0
    assert february.total_exams == 1
    assert february.revenue == 300.0
