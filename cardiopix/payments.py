from __future__ import annotations

from dataclasses import dataclass

from .models import PatientSession, PaymentStatus


class PaymentError(RuntimeError):
    pass


@dataclass
class PaymentService:
    """Encapsulates business rules for releasing reports."""

    def mark_paid(self, session: PatientSession) -> PatientSession:
        session.payment_status = PaymentStatus.PAID
        return session

    def ensure_release_allowed(self, session: PatientSession) -> None:
        if not session.allow_pdf_release():
            raise PaymentError(
                "Paciente só pode liberar o PDF após confirmação de pagamento via PIX."
            )
