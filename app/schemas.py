"""Pydantic schemas for API payloads and responses."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from .models import AuditAction


class SendMessageRequest(BaseModel):
    channel: str = Field(..., description="Destination channel, e.g. email, sms")
    message: str = Field(..., description="Body delivered to the patient or provider")


class AuditLogEntry(BaseModel):
    id: int
    hashed_user_id: str
    user_reference: Optional[str]
    action: AuditAction
    channel: str
    report_id: str
    created_at: datetime

    class Config:
        orm_mode = True


class AuditLogResponse(BaseModel):
    total: int
    items: List[AuditLogEntry]


class ComplianceFilters(BaseModel):
    user_id: Optional[str] = Field(None, description="Plain user identifier; will be hashed internally")
    action: Optional[AuditAction] = None
    channel: Optional[str] = None
    report_id: Optional[str] = None
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
