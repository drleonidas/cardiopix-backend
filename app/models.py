from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ReportStatus(str, Enum):
    PENDING = "pending"
    LAUDED = "lauded"


class Report(BaseModel):
    id: str
    patient_name: str
    status: ReportStatus = Field(default=ReportStatus.PENDING)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def mark_lauded(self) -> None:
        self.status = ReportStatus.LAUDED
        self.updated_at = datetime.utcnow()


class LaudadoEvent(BaseModel):
    report_id: str
    status: ReportStatus
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Notification(BaseModel):
    recipient: str
    subject: str
    body: str
    report_id: Optional[str] = None
    sent_at: datetime = Field(default_factory=datetime.utcnow)
