"""Audit logging utilities."""
from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import AuditAction, AuditLog
from .schemas import ComplianceFilters
from .security import hash_user_id, shorten_reference


def record_event(
    db: Session,
    *,
    user_id: str,
    action: AuditAction,
    channel: str,
    report_id: str,
) -> AuditLog:
    entry = AuditLog(
        hashed_user_id=hash_user_id(user_id),
        user_reference=shorten_reference(user_id),
        action=action,
        channel=channel,
        report_id=report_id,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def query_logs(db: Session, filters: ComplianceFilters):
    stmt = select(AuditLog)

    if filters.user_id:
        stmt = stmt.where(AuditLog.hashed_user_id == hash_user_id(filters.user_id))
    if filters.action:
        stmt = stmt.where(AuditLog.action == filters.action)
    if filters.channel:
        stmt = stmt.where(AuditLog.channel == filters.channel)
    if filters.report_id:
        stmt = stmt.where(AuditLog.report_id == filters.report_id)
    if filters.start:
        stmt = stmt.where(AuditLog.created_at >= filters.start)
    if filters.end:
        stmt = stmt.where(AuditLog.created_at <= filters.end)

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    stmt = (
        stmt.order_by(AuditLog.created_at.desc())
        .offset((filters.page - 1) * filters.page_size)
        .limit(filters.page_size)
    )
    items = db.scalars(stmt).all()
    return total or 0, items
