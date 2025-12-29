from datetime import date, datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="CardioPix Backend - Relatórios")


# Example dataset to demonstrate aggregated reports
EXAMS = [
    {
        "id": 1,
        "clinic_id": "CLIN-01",
        "clinic_name": "Clínica Central",
        "doctor_id": "DOC-01",
        "doctor_name": "Dra. Silva",
        "status": "Laudado",
        "price": 120.0,
        "exam_date": "2024-06-01",
    },
    {
        "id": 2,
        "clinic_id": "CLIN-01",
        "clinic_name": "Clínica Central",
        "doctor_id": "DOC-02",
        "doctor_name": "Dr. Pereira",
        "status": "Realizado",
        "price": 120.0,
        "exam_date": "2024-06-02",
    },
    {
        "id": 3,
        "clinic_id": "CLIN-02",
        "clinic_name": "Clínica Sul",
        "doctor_id": "DOC-01",
        "doctor_name": "Dra. Silva",
        "status": "Pendente",
        "price": 110.0,
        "exam_date": "2024-06-03",
    },
    {
        "id": 4,
        "clinic_id": "CLIN-02",
        "clinic_name": "Clínica Sul",
        "doctor_id": "DOC-03",
        "doctor_name": "Dr. Souza",
        "status": "Laudado",
        "price": 115.0,
        "exam_date": "2024-06-03",
    },
    {
        "id": 5,
        "clinic_id": "CLIN-03",
        "clinic_name": "Clínica Norte",
        "doctor_id": "DOC-03",
        "doctor_name": "Dr. Souza",
        "status": "Repetido",
        "price": 0.0,
        "exam_date": "2024-06-04",
    },
    {
        "id": 6,
        "clinic_id": "CLIN-01",
        "clinic_name": "Clínica Central",
        "doctor_id": "DOC-02",
        "doctor_name": "Dr. Pereira",
        "status": "Laudado",
        "price": 120.0,
        "exam_date": "2024-06-05",
    },
]

STATUS_KEYS = ["Realizado", "Pendente", "Repetido"]


def _parse_date(value: Optional[str], field: str) -> Optional[date]:
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value).date()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"{field} inválido, use AAAA-MM-DD") from exc


def _filter_exams(
    start_date: Optional[date],
    end_date: Optional[date],
    clinic_id: Optional[str],
    doctor_id: Optional[str],
) -> List[dict]:
    filtered: List[dict] = []
    for exam in EXAMS:
        exam_day = datetime.fromisoformat(exam["exam_date"]).date()

        if start_date and exam_day < start_date:
            continue
        if end_date and exam_day > end_date:
            continue
        if clinic_id and exam["clinic_id"] != clinic_id:
            continue
        if doctor_id and exam["doctor_id"] != doctor_id:
            continue

        filtered.append(exam)
    return filtered


def _paginate(items: List[dict], page: int, page_size: int) -> dict:
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "items": items[start:end],
        "page": page,
        "page_size": page_size,
        "total": len(items),
    }


@app.get("/reports/aggregate")
def aggregate_reports(
    start_date: Optional[str] = Query(None, description="Data inicial AAAA-MM-DD"),
    end_date: Optional[str] = Query(None, description="Data final AAAA-MM-DD"),
    clinic_id: Optional[str] = Query(None, description="Identificador da clínica"),
    doctor_id: Optional[str] = Query(None, description="Identificador do médico"),
    page: int = Query(1, ge=1, description="Página para ranking de médicos"),
    page_size: int = Query(5, ge=1, le=50, description="Itens por página"),
):
    start = _parse_date(start_date, "Data inicial")
    end = _parse_date(end_date, "Data final")

    filtered_exams = _filter_exams(start, end, clinic_id, doctor_id)

    # Contagens por status relevantes para exames
    counts = {key: 0 for key in STATUS_KEYS}
    for exam in filtered_exams:
        status = exam["status"]
        if status in counts:
            counts[status] += 1

    # Faturamento apenas de laudos concluídos (status Laudado)
    revenue = sum(exam["price"] for exam in filtered_exams if exam["status"] == "Laudado")

    # Ranking de médicos por laudos emitidos
    ranking_map = {}
    for exam in filtered_exams:
        if exam["status"] != "Laudado":
            continue
        doctor_key = exam["doctor_id"]
        ranking_map.setdefault(
            doctor_key,
            {
                "doctor_id": doctor_key,
                "doctor_name": exam["doctor_name"],
                "laudos_emitidos": 0,
            },
        )
        ranking_map[doctor_key]["laudos_emitidos"] += 1

    ranking_items = sorted(
        ranking_map.values(), key=lambda item: item["laudos_emitidos"], reverse=True
    )

    paginated_ranking = _paginate(ranking_items, page=page, page_size=page_size)

    return {
        "filters": {
            "start_date": start_date,
            "end_date": end_date,
            "clinic_id": clinic_id,
            "doctor_id": doctor_id,
        },
        "counts": counts,
        "revenue_laudos": revenue,
        "ranking": paginated_ranking,
    }


@app.get("/reports")
def reports_ui():
    return FileResponse("app/static/report.html")


app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)
