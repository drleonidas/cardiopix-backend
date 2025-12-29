from __future__ import annotations

from .models import Clinic, Laudo, Physician


class PDFGenerator:
    def generate(self, laudo: Laudo) -> bytes:
        header = (
            f"Clinica: {laudo.clinic.name} ({laudo.clinic.id})\n"
            f"Medico: {laudo.physician.name} ({laudo.physician.id})\n"
        )
        body = f"Conteudo: {laudo.content}\n"
        footer = "Documento gerado para assinatura ICP-Brasil"
        return "\n".join([header, body, footer]).encode("utf-8")
