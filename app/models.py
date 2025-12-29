"""SQLAlchemy models for audit logging and related resources."""
from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Integer, String
from sqlalchemy.sql import func

from .database import Base


class AuditAction(str, enum.Enum):
    VIEWED = "viewed"
    SENT = "sent"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    hashed_user_id = Column(String(128), index=True, nullable=False)
    user_reference = Column(String(64), nullable=True)
    action = Column(Enum(AuditAction), index=True, nullable=False)
    channel = Column(String(64), index=True, nullable=False)
    report_id = Column(String(64), index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), default=datetime.utcnow)
