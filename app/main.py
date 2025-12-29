"""CardioPix backend skeleton with audit logging for laudo access."""
from __future__ import annotations

import os
from datetime import datetime
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from . import audit
from .database import Base, engine, get_db
from .models import AuditAction
from .schemas import AuditLogResponse, ComplianceFilters, SendMessageRequest
from .security import require_compliance_token

os.makedirs("data", exist_ok=True)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CardioPix Backend")


@app.get("/reports/{report_id}/pdf")
def view_report_pdf(
    report_id: str,
    x_user_id: Annotated[str | None, Header(None)] = None,
    channel: Annotated[str, Query] = "web",
    db: Session = Depends(get_db),
):
    """Simulate report PDF retrieval and log a VIEWED action."""
    if not x_user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="x-user-id header is required")

    audit.record_event(
        db,
        user_id=x_user_id,
        action=AuditAction.VIEWED,
        channel=channel,
        report_id=report_id,
    )
    return JSONResponse({"report_id": report_id, "status": "pdf generated"})


@app.post("/reports/{report_id}/send")
def send_report(
    report_id: str,
    payload: SendMessageRequest,
    x_user_id: Annotated[str | None, Header(None)] = None,
    db: Session = Depends(get_db),
):
    """Simulate sending a report through a channel and log a SENT action."""
    if not x_user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="x-user-id header is required")

    audit.record_event(
        db,
        user_id=x_user_id,
        action=AuditAction.SENT,
        channel=payload.channel,
        report_id=report_id,
    )
    return JSONResponse({"report_id": report_id, "channel": payload.channel, "status": "sent"})


@app.get("/compliance/audit-logs", response_model=AuditLogResponse, dependencies=[Depends(require_compliance_token)])
def get_audit_logs(
    x_user_id: Annotated[str | None, Header(None)] = None,
    action: Annotated[AuditAction | None, Query] = None,
    channel: Annotated[str | None, Query] = None,
    report_id: Annotated[str | None, Query] = None,
    start: Annotated[datetime | None, Query] = None,
    end: Annotated[datetime | None, Query] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    db: Session = Depends(get_db),
):
    """Restricted compliance API with filtering and pagination."""
    filters = ComplianceFilters(
        user_id=x_user_id,
        action=action,
        channel=channel,
        report_id=report_id,
        start=start,
        end=end,
        page=page,
        page_size=page_size,
    )
    total, items = audit.query_logs(db, filters)
    return AuditLogResponse(total=total, items=items)
