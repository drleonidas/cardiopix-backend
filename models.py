from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class Physician:
    name: str
    crm: str
    rqe: Optional[str] = None
    signature_image_path: Optional[Path] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if self.signature_image_path is not None:
            data["signature_image_path"] = str(self.signature_image_path)
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Physician":
        signature_path = data.get("signature_image_path")
        return cls(
            name=data["name"],
            crm=data["crm"],
            rqe=data.get("rqe"),
            signature_image_path=Path(signature_path) if signature_path else None,
        )


@dataclass
class Laudo:
    laudo_id: str
    report_text: str
    physician: Physician
    signing_timestamp: Optional[datetime] = None
    signature_image_path: Optional[Path] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "laudo_id": self.laudo_id,
            "report_text": self.report_text,
            "physician": self.physician.to_dict(),
            "metadata": self.metadata,
        }
        if self.signing_timestamp:
            data["signing_timestamp"] = self.signing_timestamp.isoformat()
        if self.signature_image_path:
            data["signature_image_path"] = str(self.signature_image_path)
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Laudo":
        signing_ts = data.get("signing_timestamp")
        return cls(
            laudo_id=data["laudo_id"],
            report_text=data["report_text"],
            physician=Physician.from_dict(data["physician"]),
            signing_timestamp=datetime.fromisoformat(signing_ts)
            if signing_ts
            else None,
            signature_image_path=Path(data["signature_image_path"])
            if data.get("signature_image_path")
            else None,
            metadata=data.get("metadata", {}),
        )

    def with_signing(self, timestamp: datetime, signature_image_path: Optional[Path]) -> "Laudo":
        return Laudo(
            laudo_id=self.laudo_id,
            report_text=self.report_text,
            physician=self.physician,
            signing_timestamp=timestamp,
            signature_image_path=signature_image_path or self.signature_image_path,
            metadata=self.metadata,
        )
