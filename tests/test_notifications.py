from datetime import datetime

from cardiopix_backend.exam import Contact, ExamRecord, ExamStatus
from cardiopix_backend.notifications import NotificationService


def test_notification_triggered_on_laudado():
    exam = ExamRecord(
        exam_id="EX-123",
        performed_at=datetime(2026, 3, 1),
        price=250.0,
        status=ExamStatus.IN_REVIEW,
        contact=Contact(name="Maria", whatsapp="+551199999999", email="maria@example.com"),
    )
    service = NotificationService()

    change = service.handle_status_change(exam, ExamStatus.LAUDADO)

    assert change.previous_status == ExamStatus.IN_REVIEW
    assert change.new_status == ExamStatus.LAUDADO
    assert len(service.events) == 2
    channels = {event.channel for event in service.events}
    assert channels == {"whatsapp", "email"}
