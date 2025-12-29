from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI(title="CardioPix Backend Demo")


DATA_DIR = Path("data")
PDF_DIR = DATA_DIR / "pdfs"

DATA_DIR.mkdir(exist_ok=True)
PDF_DIR.mkdir(parents=True, exist_ok=True)


class LoginRequest(BaseModel):
    email: str
    password: str
    role: str


class LoginResponse(BaseModel):
    token: str
    role: str


class ExamCreateRequest(BaseModel):
    patient_name: str
    ecg_filename: Optional[str] = None


class Exam(BaseModel):
    id: int
    patient_name: str
    ecg_filename: Optional[str] = None
    status: str
    technical_data: Optional[Dict[str, str]] = None
    conclusion: Optional[str] = None
    doctor_name: Optional[str] = None
    pdf_filename: Optional[str] = None


class TechnicalFields(BaseModel):
    heart_rate: Optional[str] = None
    pr_interval: Optional[str] = None
    qrs_duration: Optional[str] = None
    qt_interval: Optional[str] = None
    rhythm: Optional[str] = None
    observations: Optional[str] = None


class ReportRequest(BaseModel):
    doctor_name: str
    technical_fields: TechnicalFields
    conclusion: str


exams: List[Exam] = []


def generate_pdf(exam: Exam) -> Path:
    """Generate a simple PDF report for the given exam."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas

    pdf_path = PDF_DIR / f"exam-{exam.id}.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=A4)

    width, height = A4
    y_position = height - 20 * mm

    # Header placeholder
    c.setFont("Helvetica-Bold", 16)
    c.drawString(20 * mm, y_position, "CardioPix - Laudo de ECG")
    c.setFont("Helvetica", 10)
    c.drawString(20 * mm, y_position - 6 * mm, "Logotipo (placeholder)")

    # Patient data
    y_position -= 20 * mm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(20 * mm, y_position, "Dados do Paciente")
    c.setFont("Helvetica", 11)
    c.drawString(20 * mm, y_position - 6 * mm, f"Nome: {exam.patient_name}")

    # Doctor data
    y_position -= 20 * mm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(20 * mm, y_position, "Médico Laudador")
    c.setFont("Helvetica", 11)
    doctor_name = exam.doctor_name or "-"
    c.drawString(20 * mm, y_position - 6 * mm, f"Nome: {doctor_name}")

    # Technical description
    y_position -= 20 * mm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(20 * mm, y_position, "Descrição Técnica")
    c.setFont("Helvetica", 11)

    y_text = y_position - 6 * mm
    if exam.technical_data:
        for label, value in exam.technical_data.items():
            c.drawString(20 * mm, y_text, f"{label}: {value}")
            y_text -= 6 * mm
    else:
        c.drawString(20 * mm, y_text, "(Não preenchido)")
        y_text -= 6 * mm

    # Conclusion
    y_text -= 6 * mm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(20 * mm, y_text, "Conclusão")
    c.setFont("Helvetica", 11)
    y_text -= 6 * mm
    c.drawString(20 * mm, y_text, exam.conclusion or "(Não preenchida)")

    c.showPage()
    c.save()
    return pdf_path


@app.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    """Mocked login that returns a pseudo token and echoes the role."""
    token = f"token-{payload.email}-{payload.role}"
    return LoginResponse(token=token, role=payload.role)


@app.post("/exams", response_model=Exam)
def create_exam(payload: ExamCreateRequest) -> Exam:
    exam_id = len(exams) + 1
    exam = Exam(
        id=exam_id,
        patient_name=payload.patient_name,
        ecg_filename=payload.ecg_filename,
        status="aguardando_laudo",
    )
    exams.append(exam)
    return exam


@app.get("/exams/queue", response_model=List[Exam])
def get_queue() -> List[Exam]:
    return [exam for exam in exams if exam.status == "aguardando_laudo"]


@app.post("/exams/{exam_id}/report")
def finalize_report(exam_id: int, payload: ReportRequest) -> Dict[str, str]:
    exam = next((item for item in exams if item.id == exam_id), None)
    if not exam:
        raise HTTPException(status_code=404, detail="Exame não encontrado")

    exam.doctor_name = payload.doctor_name
    exam.technical_data = {
        "Frequência Cardíaca": payload.technical_fields.heart_rate or "",
        "Intervalo PR": payload.technical_fields.pr_interval or "",
        "Duração do QRS": payload.technical_fields.qrs_duration or "",
        "Intervalo QT": payload.technical_fields.qt_interval or "",
        "Ritmo": payload.technical_fields.rhythm or "",
        "Observações": payload.technical_fields.observations or "",
    }
    exam.conclusion = payload.conclusion
    exam.status = "laudo_finalizado"

    pdf_path = generate_pdf(exam)
    exam.pdf_filename = pdf_path.name
    pdf_url = f"/pdfs/{pdf_path.name}"
    return {"pdf_url": pdf_url}


@app.get("/pdfs/{filename}")
def get_pdf(filename: str):
    file_path = PDF_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="PDF não encontrado")
    return FileResponse(file_path, media_type="application/pdf")
