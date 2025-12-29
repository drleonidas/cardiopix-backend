from __future__ import annotations

import uuid
from typing import Optional

from .models import Clinic, Laudo, Physician, SignatureRequest


class SignerClient:
    """Simulates a connector to an ICP-Brasil compliant signing service."""

    def request_signature(
        self,
        pdf_bytes: bytes,
        physician: Physician,
        clinic: Clinic,
        laudo: Laudo,
    ) -> SignatureRequest:
        request_id = str(uuid.uuid4())
        return SignatureRequest(id=request_id, laudo_id=laudo.id)

    def download_signed_pdf(self, request_id: str) -> Optional[bytes]:
        return None
