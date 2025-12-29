from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


class LaudoStatus(Enum):
    DRAFT = auto()
    PENDING_SIGNATURE = auto()
    SIGNED = auto()
    SIGNATURE_FAILED = auto()


@dataclass
class Physician:
    id: str
    name: str
    certificate_path: str


@dataclass
class Clinic:
    id: str
    name: str


@dataclass
class Laudo:
    id: str
    physician: Physician
    clinic: Clinic
    content: str
    status: LaudoStatus = LaudoStatus.DRAFT
    pdf_bytes: Optional[bytes] = None
    signature_request_id: Optional[str] = None
    signed_pdf_bytes: Optional[bytes] = None
    failure_reason: Optional[str] = None


@dataclass
class SignatureRequest:
    id: str
    laudo_id: str


@dataclass
class SignatureCallback:
    request_id: str
    succeeded: bool
    signed_pdf_bytes: Optional[bytes] = None
    error_message: Optional[str] = None
    metadata: dict = field(default_factory=dict)
