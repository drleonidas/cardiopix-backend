from __future__ import annotations

from typing import Dict, Optional

from .models import Laudo


class InMemoryLaudoRepository:
    def __init__(self) -> None:
        self._laudos: Dict[str, Laudo] = {}

    def add(self, laudo: Laudo) -> None:
        self._laudos[laudo.id] = laudo

    def get(self, laudo_id: str) -> Optional[Laudo]:
        return self._laudos.get(laudo_id)

    def update(self, laudo: Laudo) -> None:
        if laudo.id not in self._laudos:
            raise KeyError(f"Laudo {laudo.id} not found")
        self._laudos[laudo.id] = laudo
