from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from .context import ClinicContextProvider, ClinicContext


@dataclass
class RenderContext:
    """Aggregates the dynamic data passed to the laudo template."""

    body: Dict[str, Any]
    clinic: ClinicContext

    @property
    def header(self) -> Dict[str, Any]:
        logo_markup: str
        if self.clinic.logo_exists:
            logo_markup = f'<img class="clinic-logo" src="{self.clinic.logo_path}" alt="Logo da clínica" />'
        else:
            logo_markup = "<div class=\"clinic-logo missing\">Sem logotipo</div>"

        address = self.clinic.address or "Endereço não informado"
        return {
            "clinic_name": self.clinic.name,
            "logo_markup": logo_markup,
            "address": address,
        }

    @property
    def footer(self) -> Dict[str, Any]:
        return {
            "address": self.clinic.address or "Endereço não informado",
        }


class ReportPDFGenerator:
    """High-level pipeline that renders laudo PDFs from a template."""

    def __init__(
        self,
        template_path: Path,
        output_dir: Path,
        clinic_registry: Path,
    ) -> None:
        self.template_path = template_path
        self.output_dir = output_dir
        self._clinic_provider = ClinicContextProvider(clinic_registry)

    def render(self, report_id: str, clinic_id: str, body_payload: Dict[str, Any]) -> Path:
        render_context = RenderContext(
            body=body_payload,
            clinic=self._clinic_provider.get_context(clinic_id),
        )
        rendered_html = self._render_template(render_context)
        return self._write_pdf(report_id, rendered_html)

    def _render_template(self, context: RenderContext) -> str:
        template = self.template_path.read_text(encoding="utf-8")
        return template.format(
            clinic_name=context.header["clinic_name"],
            clinic_logo=context.header["logo_markup"],
            clinic_address=context.header["address"],
            report_body=context.body.get("html", ""),
            footer_address=context.footer["address"],
        )

    def _write_pdf(self, report_id: str, rendered_html: str) -> Path:
        """Persist the rendered markup as a PDF-ready artifact.

        In production we would send this HTML to a PDF engine such as wkhtmltopdf
        or WeasyPrint. For this scaffold we persist the HTML to a .pdf file so it
        can be inspected and handed off to a renderer by the hosting platform.
        """

        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.output_dir / f"{report_id}.pdf"
        output_path.write_text(rendered_html, encoding="utf-8")
        return output_path
