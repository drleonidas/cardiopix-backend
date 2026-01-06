from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional


@dataclass
class ClinicContext:
    """Represents the clinic-specific data injected into reports."""

    id: str
    name: str
    logo_path: Optional[Path]
    address: Optional[str]

    @property
    def logo_exists(self) -> bool:
        return bool(self.logo_path and self.logo_path.exists())

    @property
    def has_address(self) -> bool:
        return bool(self.address)


class ClinicContextProvider:
    """Loads clinic metadata for use in laudo rendering.

    This default implementation reads from a JSON file so the renderer
    can be used without a database. A real application could replace
    this provider with one backed by an ORM.
    """

    def __init__(self, clinic_registry: Path):
        self._clinic_registry = clinic_registry

    def get_context(self, clinic_id: str) -> ClinicContext:
        data = self._load_registry().get(clinic_id)
        if not data:
            return ClinicContext(id=clinic_id, name=clinic_id, logo_path=None, address=None)

        logo_path = Path(data["logo_path"]) if data.get("logo_path") else None
        address = data.get("address") or None
        return ClinicContext(
            id=clinic_id,
            name=data.get("name", clinic_id),
            logo_path=logo_path,
            address=address,
        )

    def _load_registry(self) -> Dict[str, Dict[str, str]]:
        if not self._clinic_registry.exists():
            return {}
        with self._clinic_registry.open("r", encoding="utf-8") as fp:
            return json.load(fp)
