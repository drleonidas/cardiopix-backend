"""Security helpers for compliance endpoints and data minimization."""
from __future__ import annotations

import hashlib
import os
from typing import Optional

from fastapi import Header, HTTPException, status

COMPLIANCE_TOKEN = os.getenv("COMPLIANCE_TOKEN", "change-me")
AUDIT_SALT = os.getenv("AUDIT_SALT", "cardiopix-salt")


def require_compliance_token(x_compliance_token: Optional[str] = Header(None)) -> None:
    """Simple token-based guard for the compliance API."""
    if not x_compliance_token or x_compliance_token != COMPLIANCE_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: compliance token is missing or invalid.",
        )


def hash_user_id(user_id: str) -> str:
    """Create a deterministic, salted hash to avoid storing raw identifiers."""
    digest = hashlib.sha256()
    digest.update(f"{AUDIT_SALT}:{user_id}".encode("utf-8"))
    return digest.hexdigest()


def shorten_reference(user_id: str) -> str:
    """Return a shortened reference (last four characters) for audit review."""
    return user_id[-4:] if len(user_id) >= 4 else user_id
