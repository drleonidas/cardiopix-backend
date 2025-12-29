from typing import List

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect

from .models import LaudadoEvent, Report, ReportStatus
from .notifications import NotificationService
from .store import InMemoryReportStore
from .websocket_manager import WebSocketManager

app = FastAPI(title="CardioPix Backend")
store = InMemoryReportStore()
websocket_manager = WebSocketManager()
notification_service = NotificationService(websocket_manager)


def bootstrap() -> None:
    seed_reports = [
        Report(id="1001", patient_name="Maria da Silva"),
        Report(id="1002", patient_name="João Souza"),
    ]
    store.seed(seed_reports)


bootstrap()


@app.get("/reports", response_model=List[Report])
def list_reports() -> List[Report]:
    return store.list_reports()


@app.post("/reports/{report_id}/complete", response_model=Report)
async def complete_report(report_id: str) -> Report:
    try:
        report = store.mark_lauded(report_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    event = LaudadoEvent(report_id=report.id, status=ReportStatus.LAUDED)
    await notification_service.notify_laudado(event, recipient="clinica@cardiopix.local")
    return report


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await websocket_manager.disconnect(websocket)
