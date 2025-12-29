from pathlib import Path
from datetime import datetime
from typing import Optional

from fpdf import FPDF

BASE_DIR = Path(__file__).resolve().parent.parent
PDF_STORAGE_DIR = BASE_DIR / "storage" / "pdfs"


class ReportFinalizePayload:
    """Simple container for data used to render a PDF."""

    def __init__(self, patient_name: str, report_summary: str, clinician_name: Optional[str] = None):
        self.patient_name = patient_name
        self.report_summary = report_summary
        self.clinician_name = clinician_name


def ensure_storage_dir() -> None:
    PDF_STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def get_pdf_path(report_id: str) -> Path:
    return PDF_STORAGE_DIR / f"{report_id}.pdf"


def generate_report_pdf(report_id: str, payload: ReportFinalizePayload) -> Path:
    """Generate a simple PDF for the report data and return its file path."""

    ensure_storage_dir()
    pdf_path = get_pdf_path(report_id)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=16)
    pdf.cell(0, 10, "CardioPix - Laudo de ECG", ln=True, align="C")

    pdf.set_font("Helvetica", size=12)
    pdf.ln(8)
    pdf.cell(0, 10, f"Paciente: {payload.patient_name}", ln=True)
    pdf.cell(0, 10, f"Data: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", ln=True)

    pdf.ln(8)
    pdf.multi_cell(0, 10, f"Resumo do laudo:\n{payload.report_summary}")

    if payload.clinician_name:
        pdf.ln(8)
        pdf.cell(0, 10, f"Responsável: {payload.clinician_name}", ln=True)

    pdf.output(pdf_path)

    return pdf_path
