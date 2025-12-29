from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

from fpdf import FPDF

from models import Laudo

PDF_OUTPUT_DIR = Path("data/pdfs")
PDF_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class LaudoPdf(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "Laudo Médico", ln=True, align="C")
        self.ln(5)


def _render_signature_block(pdf: FPDF, laudo: Laudo) -> None:
    signature_used = laudo.signature_image_path or laudo.physician.signature_image_path

    if signature_used and Path(signature_used).exists():
        pdf.image(str(signature_used), x=10, y=None, h=25)
    pdf.ln(28 if signature_used else 5)

    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, f"CRM: {laudo.physician.crm}", ln=True)
    if laudo.physician.rqe:
        pdf.cell(0, 8, f"RQE: {laudo.physician.rqe}", ln=True)


def _render_timestamp(pdf: FPDF, signing_timestamp: Optional[datetime]) -> None:
    pdf.ln(3)
    pdf.set_font("Helvetica", "I", 9)
    if signing_timestamp:
        pdf.cell(0, 6, f"Assinado digitalmente em: {signing_timestamp.isoformat()}", ln=True)
    else:
        pdf.cell(0, 6, "Assinatura digital pendente", ln=True)


def render_laudo_pdf(laudo: Laudo, output_path: Optional[Path] = None) -> Path:
    pdf = LaudoPdf()
    pdf.add_page()

    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 8, laudo.report_text)

    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, laudo.physician.name, ln=True)

    _render_signature_block(pdf, laudo)
    _render_timestamp(pdf, laudo.signing_timestamp)

    output = output_path or (PDF_OUTPUT_DIR / f"{laudo.laudo_id}.pdf")
    pdf.output(str(output))
    return output
