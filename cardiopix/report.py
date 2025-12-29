"""Report payload helpers for CardioPix.

The helpers here are designed to be framework-agnostic so they can be used from
API routes, background workers, or CLI tools.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping


class PhysicianIdentifiersMissing(ValueError):
    """Raised when required physician identifiers are not available."""

    def __init__(self, missing_fields: list[str]):
        fields = ", ".join(missing_fields)
        super().__init__(f"Missing physician identifiers: {fields}")
        self.missing_fields = missing_fields


@dataclass(frozen=True)
class Responsibility:
    """Data about the physician responsible for the laudo."""

    name: str
    crm: str
    crm_uf: str
    rqe: str

    @classmethod
    def from_session(cls, session: Mapping[str, Any]) -> "Responsibility":
        """Build a Responsibility object from a login session.

        Args:
            session: Mapping containing login session details.

        Raises:
            PhysicianIdentifiersMissing: When required identifiers are absent.
        """

        missing: list[str] = []
        name = str(session.get("physician_name") or "").strip()
        crm = str(session.get("physician_crm") or "").strip()
        crm_uf = str(session.get("physician_crm_uf") or "").strip()
        rqe = str(session.get("physician_rqe") or "").strip()

        if not crm:
            missing.append("CRM")
        if not crm_uf:
            missing.append("CRM_UF")
        if not rqe:
            missing.append("RQE")

        if missing:
            raise PhysicianIdentifiersMissing(missing)

        return cls(name=name, crm=crm, crm_uf=crm_uf, rqe=rqe)

    def to_payload(self) -> Dict[str, str]:
        """Convert responsibility information to a serializable payload."""

        return {
            "physician_name": self.name,
            "physician_crm": self.crm,
            "physician_crm_uf": self.crm_uf,
            "physician_rqe": self.rqe,
            "responsibility": f"Dr(a). {self.name} - CRM {self.crm}/{self.crm_uf} - RQE {self.rqe}",
        }


class LaudoPayloadBuilder:
    """Builds laudo payloads enriched with responsibility data."""

    def __init__(self, session: Mapping[str, Any]):
        self.session = session

    def build(self, base_payload: Mapping[str, Any]) -> Dict[str, Any]:
        """Return a laudo payload including physician responsibility info.

        Args:
            base_payload: Minimal laudo data collected from generation flow.

        Raises:
            PhysicianIdentifiersMissing: When CRM, CRM UF, or RQE is missing in
                the session.
        """

        responsibility = Responsibility.from_session(self.session)
        payload: Dict[str, Any] = dict(base_payload)
        payload.update(responsibility.to_payload())
        payload.setdefault("responsibility_section", responsibility.to_payload())
        return payload
