from __future__ import annotations

import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from models import Laudo

SIGNATURE_DIR = Path("data/signatures")
SIGNATURE_DIR.mkdir(parents=True, exist_ok=True)


class SigningError(Exception):
    """Raised when the signing response does not include required data."""


def _persist_signature_image(signature_b64: Optional[str], laudo_id: str) -> Optional[Path]:
    if not signature_b64:
        return None

    filename = SIGNATURE_DIR / f"{laudo_id}_signature.png"
    binary = base64.b64decode(signature_b64)
    filename.write_bytes(binary)
    return filename


def apply_signing_response(laudo: Laudo, signing_response: Dict[str, str]) -> Laudo:
    """
    Capture the timestamp and signature image from a digital signing response.

    The response is expected to contain an ISO8601 timestamp and a base64-encoded
    PNG signature under the keys ``timestamp`` and ``signature_image``.
    """

    if "timestamp" not in signing_response:
        raise SigningError("Signing response missing required timestamp field")

    timestamp = datetime.fromisoformat(signing_response["timestamp"])
    signature_image_path = _persist_signature_image(
        signing_response.get("signature_image"), laudo.laudo_id
    )

    return laudo.with_signing(timestamp=timestamp, signature_image_path=signature_image_path)
