from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class PaymentMethod(str, Enum):
    PIX = "PIX"
    MANUAL = "MANUAL"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"


class BillingOption(str, Enum):
    ANTECIPADO = "Antecipado"
    NO_ATO = "No Ato"
    FATURADO = "Faturado"


@dataclass
class Clinic:
    name: str
    brand: str
    technical_manager: str
    technical_id: str
    billing_option: Optional[BillingOption] = None


@dataclass
class Doctor:
    name: str
    registry: str
    brand: Optional[str] = None


@dataclass
class PatientSession:
    patient_name: str
    payment_method: PaymentMethod
    payment_status: PaymentStatus = PaymentStatus.PENDING

    def allow_pdf_release(self) -> bool:
        """Only allow release after PIX payment is completed."""
        if self.payment_method != PaymentMethod.PIX:
            return False
        return self.payment_status == PaymentStatus.PAID


@dataclass
class HealthUnitRegistration:
    clinic: Clinic
    billing_option: BillingOption

    def __post_init__(self) -> None:
        self.clinic.billing_option = self.billing_option
