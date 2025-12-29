from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .pdf_service import ReportFinalizePayload, generate_report_pdf, get_pdf_path, ensure_storage_dir

app = FastAPI(title="CardioPix Backend")


class FinalizePayload(BaseModel):
    patient_name: str
    report_summary: str
    clinician_name: str | None = None


@app.on_event("startup")
def prepare_storage() -> None:
    ensure_storage_dir()


@app.post("/reports/{report_id}/finalize")
def finalize_report(report_id: str, payload: FinalizePayload):
    pdf_path = generate_report_pdf(
        report_id=report_id,
        payload=ReportFinalizePayload(
            patient_name=payload.patient_name,
            report_summary=payload.report_summary,
            clinician_name=payload.clinician_name,
        ),
    )

    pdf_url = f"/reports/{report_id}/pdf"
    return {
        "status": "finalized",
        "pdfUrl": pdf_url,
        "pdfPath": str(pdf_path),
    }


@app.get("/reports/{report_id}/pdf")
def fetch_pdf(report_id: str):
    pdf_path = get_pdf_path(report_id)
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF não encontrado")

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=pdf_path.name,
        headers={"Content-Disposition": f"inline; filename={pdf_path.name}"},
    )


@app.get("/")
def healthcheck():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
