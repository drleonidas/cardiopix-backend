"""Exam domain models and status handling."""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class ExamStatus(str, Enum):
    SCHEDULED = "Agendado"
    IN_REVIEW = "Em análise"
    LAUDADO = "Laudado"
    DELIVERED = "Entregue"


@dataclass
class Contact:
    name: str
    whatsapp: Optional[str] = None
    email: Optional[str] = None


@dataclass
class ExamRecord:
    exam_id: str
    performed_at: datetime
    price: float
    status: ExamStatus
    contact: Contact


@dataclass
class StatusChange:
    exam: ExamRecord
    previous_status: ExamStatus
    new_status: ExamStatus
    changed_at: datetime
