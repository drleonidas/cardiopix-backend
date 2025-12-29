from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from sqlalchemy.orm import Session

from app.config import Settings
from app.models import DeliveryLog
from app.schemas import ExamCompletionPayload
from app.services.messaging import MessageChannelError, MessagingService
from app.services.pdf import PDFGenerationResult

logger = logging.getLogger(__name__)


@dataclass
class NotificationResult:
    channel: str
    recipient: str
    status: str
    attempt: int
    message_id: str | None
    error_message: str | None


class NotificationManager:
    def __init__(self, settings: Settings, session: Session):
        self.settings = settings
        self.session = session
        self.messaging = MessagingService(settings)

    def send_notifications(self, payload: ExamCompletionPayload, pdf_result: PDFGenerationResult) -> list[NotificationResult]:
        results: list[NotificationResult] = []
        channels = self._iter_channels(payload)
        for channel, recipient in channels:
            result = self._dispatch_with_retry(channel, recipient, payload, pdf_result)
            results.append(result)
        return results

    def _iter_channels(self, payload: ExamCompletionPayload) -> Iterable[tuple[str, str]]:
        if payload.patient.whatsapp:
            yield ("whatsapp", payload.patient.whatsapp)
        if payload.patient.email:
            yield ("email", payload.patient.email)

    def _dispatch_with_retry(
        self, channel: str, recipient: str, payload: ExamCompletionPayload, pdf_result: PDFGenerationResult
    ) -> NotificationResult:
        attempts = 0
        message_id: str | None = None
        error_message: str | None = None
        status = "failed"

        while attempts < self.settings.max_delivery_attempts:
            attempts += 1
            try:
                if channel == "whatsapp":
                    message_id = self.messaging.send_whatsapp(to=recipient, body=self._render_message(payload, pdf_result))
                else:
                    subject = f"Exame {payload.exam_id} concluído"
                    message_id = self.messaging.send_email(
                        to=recipient, subject=subject, body=self._render_message(payload, pdf_result)
                    )
                status = "delivered"
                error_message = None
                break
            except MessageChannelError as exc:  # pragma: no cover - placeholder for real provider errors
                error_message = str(exc)
                logger.warning("Delivery attempt %s for %s via %s failed: %s", attempts, recipient, channel, exc)
                time.sleep(self.settings.retry_backoff_seconds * attempts)

        self._persist_log(
            exam_id=payload.exam_id,
            recipient=recipient,
            channel=channel,
            status=status,
            attempt=attempts,
            message_id=message_id,
            error_message=error_message,
        )

        if status != "delivered":
            self._alert_failure(exam_id=payload.exam_id, recipient=recipient, channel=channel, error_message=error_message)

        return NotificationResult(
            channel=channel,
            recipient=recipient,
            status=status,
            attempt=attempts,
            message_id=message_id,
            error_message=error_message,
        )

    def _persist_log(
        self,
        exam_id: str,
        recipient: str,
        channel: str,
        status: str,
        attempt: int,
        message_id: str | None,
        error_message: str | None,
    ) -> None:
        log_entry = DeliveryLog(
            exam_id=exam_id,
            recipient=recipient,
            channel=channel,
            status=status,
            attempt=attempt,
            message_id=message_id,
            error_message=error_message,
            created_at=datetime.utcnow(),
        )
        self.session.add(log_entry)
        self.session.commit()

    def _alert_failure(self, exam_id: str, recipient: str, channel: str, error_message: str | None) -> None:
        logger.error(
            "Delivery failure for exam %s to %s via %s. Error: %s",
            exam_id,
            recipient,
            channel,
            error_message or "unknown",
        )

    def _render_message(self, payload: ExamCompletionPayload, pdf_result: PDFGenerationResult) -> str:
        signed_at = payload.exam_signed_at.isoformat() if payload.exam_signed_at else datetime.utcnow().isoformat()
        return (
            f"Olá {payload.patient.name}, seu laudo do exame {payload.exam_id} foi assinado em {signed_at}.\n"
            f"Resumo: {payload.report_summary or 'N/A'}.\n"
            f"Baixe o PDF em: {pdf_result.download_url}"
        )
