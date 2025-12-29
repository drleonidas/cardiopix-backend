"""Notification utilities for status-driven alerts."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from .exam import ExamRecord, ExamStatus, StatusChange


@dataclass
class NotificationEvent:
    channel: str
    destination: str
    message: str
    sent_at: datetime


@dataclass
class NotificationService:
    """Simple in-memory dispatcher for WhatsApp and email."""

    events: List[NotificationEvent] = field(default_factory=list)

    def send_whatsapp(self, destination: str, message: str) -> None:
        self._register("whatsapp", destination, message)

    def send_email(self, destination: str, message: str) -> None:
        self._register("email", destination, message)

    def handle_status_change(self, exam: ExamRecord, new_status: ExamStatus) -> StatusChange:
        """Update status and dispatch notifications when applicable."""

        previous_status = exam.status
        exam.status = new_status
        change = StatusChange(
            exam=exam,
            previous_status=previous_status,
            new_status=new_status,
            changed_at=datetime.utcnow(),
        )

        if new_status == ExamStatus.LAUDADO:
            self._notify_laudado(exam)

        return change

    def _notify_laudado(self, exam: ExamRecord) -> None:
        message = (
            f"Olá {exam.contact.name}, seu exame {exam.exam_id} foi laudado e está disponível para consulta."
        )
        if exam.contact.whatsapp:
            self.send_whatsapp(exam.contact.whatsapp, message)
        if exam.contact.email:
            self.send_email(exam.contact.email, message)

    def _register(self, channel: str, destination: str, message: str) -> None:
        self.events.append(
            NotificationEvent(
                channel=channel,
                destination=destination,
                message=message,
                sent_at=datetime.utcnow(),
            )
        )
