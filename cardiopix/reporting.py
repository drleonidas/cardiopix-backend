from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .models import Clinic, Doctor


PAGE_HEIGHT_PT = 842  # A4 height in points
LINE_HEIGHT = 14
FOOTER_MARGIN = 72


@dataclass
class ReportRequest:
    clinic: Clinic
    doctor: Doctor
    patient_name: str
    findings: str
    brand_override: Optional[str] = None

    @property
    def branding(self) -> str:
        return self.brand_override or self.doctor.brand or self.clinic.brand

    @property
    def technical_responsibility(self) -> str:
        return f"Responsável técnico: {self.clinic.technical_manager} - {self.clinic.technical_id}"

    @property
    def signature_line(self) -> str:
        return f"Assinado digitalmente por {self.doctor.name} (CRM {self.doctor.registry})"


@dataclass
class ReportLayout:
    signature_y: float
    page_height: float
    branding: str
    technical_responsibility: str

    @property
    def is_signature_in_footer(self) -> bool:
        return self.signature_y >= (self.page_height - FOOTER_MARGIN)


class ReportService:
    def __init__(self, output_dir: Path) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_pdf(self, request: ReportRequest, filename: str = "report.pdf") -> ReportLayout:
        path = self.output_dir / filename

        header = f"Marca: {request.branding}\n{request.technical_responsibility}\n"
        body = (
            "Conteúdo do laudo:\n"
            f"{request.findings}\n\n"
            "Assinatura posicionada no rodapé para garantir espaçamento visual."
        )

        signature_y = PAGE_HEIGHT_PT - FOOTER_MARGIN
        footer = (
            f"\n\n[Assinatura]\n{request.signature_line}\nPaciente: {request.patient_name}\n"
        )

        path.write_text(header + body + footer, encoding="utf-8")

        return ReportLayout(
            signature_y=signature_y,
            page_height=PAGE_HEIGHT_PT,
            branding=request.branding,
            technical_responsibility=request.technical_responsibility,
        )
