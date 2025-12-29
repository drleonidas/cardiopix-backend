from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Integer, String

from app.database import Base


class DeliveryLog(Base):
    __tablename__ = "delivery_logs"

    id: int = Column(Integer, primary_key=True, index=True)
    exam_id: str = Column(String, index=True, nullable=False)
    recipient: str = Column(String, nullable=False)
    channel: str = Column(String, nullable=False)
    status: str = Column(String, nullable=False)
    attempt: int = Column(Integer, nullable=False, default=1)
    message_id: Optional[str] = Column(String)
    error_message: Optional[str] = Column(String)
    created_at: datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
