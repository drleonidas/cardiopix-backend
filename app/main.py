from __future__ import annotations

import logging
from pathlib import Path

from fastapi import BackgroundTasks, Depends, FastAPI
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import Base, engine, get_db
from app.schemas import DeliveryLogRead, ExamCompletionPayload
from app.services.notifications import NotificationManager
from app.services.pdf import PDFGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CardioPix Notifications")
pdf_generator = PDFGenerator(output_dir=Path("data/reports"))


@app.post("/events/exams/completed")
async def handle_exam_completed(
    payload: ExamCompletionPayload, background_tasks: BackgroundTasks, session: Session = Depends(get_db)
):
    pdf_result = pdf_generator.generate_report(exam_id=payload.exam_id, report_summary=payload.report_summary)
    notification_manager = NotificationManager(settings=settings, session=session)
    background_tasks.add_task(notification_manager.send_notifications, payload, pdf_result)
    return {
        "status": "queued",
        "pdf": {"path": str(pdf_result.file_path), "download_url": pdf_result.download_url},
    }


@app.get("/reports/{filename}")
async def download_report(filename: str):
    file_path = Path("data/reports") / filename
    if not file_path.exists():
        return {"error": "Report not found"}
    return FileResponse(file_path)


@app.get("/delivery-logs", response_model=list[DeliveryLogRead])
async def list_delivery_logs(session: Session = Depends(get_db)):
    from app.models import DeliveryLog

    logs = session.query(DeliveryLog).order_by(DeliveryLog.created_at.desc()).all()
    return logs
