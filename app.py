from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from models import Laudo, Physician
from services.pdf import render_laudo_pdf
from services.signing import apply_signing_response

LAUDOS_DB = Path("data/laudos.json")


def save_laudo(laudo: Laudo) -> None:
    existing: Dict[str, Dict] = {}
    if LAUDOS_DB.exists():
        existing = json.loads(LAUDOS_DB.read_text())

    existing[laudo.laudo_id] = laudo.to_dict()
    LAUDOS_DB.write_text(json.dumps(existing, indent=2, ensure_ascii=False))


def load_laudo(laudo_id: str) -> Laudo:
    data = json.loads(LAUDOS_DB.read_text())
    if laudo_id not in data:
        raise KeyError(f"Laudo {laudo_id} not found")
    return Laudo.from_dict(data[laudo_id])


def create_signed_laudo(laudo_id: str, report_text: str, physician_data: Dict[str, str], signing_response: Dict[str, str]):
    physician = Physician(**physician_data)
    laudo = Laudo(laudo_id=laudo_id, report_text=report_text, physician=physician)

    laudo = apply_signing_response(laudo, signing_response)
    save_laudo(laudo)

    pdf_path = render_laudo_pdf(laudo)
    return laudo, pdf_path


if __name__ == "__main__":
    # Example usage for manual testing
    sample_laudo_id = "laudo-123"
    sample_report = "Paciente apresenta ECG dentro da normalidade. Sem alterações relevantes."
    physician_payload = {
        "name": "Dra. Ana Silva",
        "crm": "12345",
        "rqe": "67890",
    }

    sample_signing_response = {
        "timestamp": "2024-05-01T10:15:00",
        # Replace with real base64 from signing provider when available
        "signature_image": "",
    }

    laudo, pdf_path = create_signed_laudo(
        laudo_id=sample_laudo_id,
        report_text=sample_report,
        physician_data=physician_payload,
        signing_response=sample_signing_response,
    )
    print(f"Laudo salvo em {LAUDOS_DB}")
    print(f"PDF gerado em {pdf_path}")
