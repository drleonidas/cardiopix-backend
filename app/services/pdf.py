from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class PDFGenerationResult:
    file_path: Path
    download_url: str
    generated_at: datetime


class PDFGenerator:
    """Wrapper for an existing PDF generator."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_report(self, exam_id: str, report_summary: str | None) -> PDFGenerationResult:
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        filename = f"exam_{exam_id}_{timestamp}.pdf"
        file_path = self.output_dir / filename
        placeholder_content = (
            f"Relatório do exame {exam_id}\n"
            f"Gerado em: {datetime.utcnow().isoformat()}\n\n"
            f"Resumo: {report_summary or 'N/A'}\n"
        )
        file_path.write_text(placeholder_content, encoding="utf-8")
        return PDFGenerationResult(file_path=file_path, download_url=f"/reports/{filename}", generated_at=datetime.utcnow())


__all__ = ["PDFGenerator", "PDFGenerationResult"]
