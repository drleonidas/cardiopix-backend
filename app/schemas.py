from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class PatientContact(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    whatsapp: Optional[str] = Field(None, description="Número no formato E.164")


class ExamCompletionPayload(BaseModel):
    exam_id: str
    patient: PatientContact
    report_summary: Optional[str] = None
    exam_signed_at: Optional[datetime] = None


class DeliveryLogRead(BaseModel):
    id: int
    exam_id: str
    recipient: str
    channel: str
    status: str
    attempt: int
    message_id: Optional[str]
    error_message: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True
