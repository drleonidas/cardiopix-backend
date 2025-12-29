"""
Serviço para renderização de laudos em PDF.

Este módulo define uma API simples para receber dados do exame,
 paciente e médico laudador e gerar um PDF formatado a partir de um
 template HTML. A renderização é feita via WeasyPrint para manter o
 controle de margens, tipografia e separadores.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import CSS, HTML


TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
DEFAULT_TEMPLATE = "laudo.html"
DEFAULT_STYLESHEET = "laudo.css"


@dataclass
class PatientData:
    """Informações do paciente que aparecerão no laudo."""

    nome: str
    data_nascimento: str
    sexo: Optional[str] = None
    identificador: Optional[str] = None


@dataclass
class DoctorData:
    """Informações do médico laudador."""

    nome: str
    crm: Optional[str] = None
    especialidade: Optional[str] = None


@dataclass
class ExamData:
    """Dados técnicos e conclusão do exame."""

    descricao_tecnica: str
    conclusao: str
    data_exame: Optional[str] = None
    protocolo: Optional[str] = None


class LaudoPdfService:
    """Serviço responsável por gerar PDFs a partir do template padrão."""

    def __init__(
        self,
        *,
        template_name: str = DEFAULT_TEMPLATE,
        stylesheet_name: str = DEFAULT_STYLESHEET,
    ) -> None:
        self.template_name = template_name
        self.stylesheet_name = stylesheet_name
        self.env = Environment(
            loader=FileSystemLoader(str(TEMPLATE_DIR)),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def _build_context(
        self,
        *,
        paciente: PatientData,
        medico: DoctorData,
        exame: ExamData,
        extras: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        context: Dict[str, Any] = {
            "paciente": paciente,
            "medico": medico,
            "exame": exame,
        }
        if extras:
            context.update(extras)
        return context

    def render_html(
        self,
        *,
        paciente: PatientData,
        medico: DoctorData,
        exame: ExamData,
        extras: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Gera HTML do laudo a partir do template configurado."""

        template = self.env.get_template(self.template_name)
        context = self._build_context(
            paciente=paciente, medico=medico, exame=exame, extras=extras
        )
        return template.render(**context)

    def render_pdf(
        self,
        *,
        paciente: PatientData,
        medico: DoctorData,
        exame: ExamData,
        extras: Optional[Dict[str, Any]] = None,
        output_path: Optional[Path] = None,
    ) -> bytes:
        """Renderiza o laudo em PDF e retorna o conteúdo em bytes.

        Args:
            paciente: Dados do paciente.
            medico: Dados do médico laudador.
            exame: Dados técnicos e conclusão do exame.
            extras: Campos adicionais para o template.
            output_path: Caminho opcional para salvar o PDF gerado.
        """

        html_str = self.render_html(
            paciente=paciente, medico=medico, exame=exame, extras=extras
        )

        html = HTML(string=html_str, base_url=str(TEMPLATE_DIR))
        stylesheet_path = TEMPLATE_DIR / self.stylesheet_name
        stylesheets = [CSS(filename=str(stylesheet_path))]

        return html.write_pdf(target=str(output_path) if output_path else None, stylesheets=stylesheets)


def generate_laudo_pdf(
    *,
    paciente: PatientData,
    medico: DoctorData,
    exame: ExamData,
    extras: Optional[Dict[str, Any]] = None,
    output_path: Optional[Path] = None,
) -> bytes:
    """Helper para geração rápida de laudos com o template padrão."""

    service = LaudoPdfService()
    return service.render_pdf(
        paciente=paciente, medico=medico, exame=exame, extras=extras, output_path=output_path
    )
