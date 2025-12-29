from .models import LaudadoEvent, Notification
from .websocket_manager import WebSocketManager


class NotificationService:
    def __init__(self, websocket_manager: WebSocketManager) -> None:
        self.websocket_manager = websocket_manager

    async def notify_laudado(self, event: LaudadoEvent, recipient: str) -> Notification:
        notification = Notification(
            recipient=recipient,
            subject="Laudo concluído",
            body=f"O laudo do exame {event.report_id} foi concluído com status {event.status.value}.",
            report_id=event.report_id,
        )
        await self.websocket_manager.broadcast({
            "type": "report_laudado",
            "payload": notification.dict(),
        })
        return notification
