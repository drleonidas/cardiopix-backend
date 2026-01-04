from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cardiopix import Clinic, Doctor, ReportRequest, ReportService


if __name__ == "__main__":
    output_dir = ROOT / "reports"
    clinic = Clinic(
        name="Clínica Solar",
        brand="CardioPix | Clínica Solar",
        technical_manager="Dra. Ana Lima",
        technical_id="CRM 0001",
    )
    doctor = Doctor(name="Dr. Breno Costa", registry="0002")

    report = ReportRequest(
        clinic=clinic,
        doctor=doctor,
        patient_name="Maria da Silva",
        findings=(
            "Eletrocardiograma com ritmo sinusal, frequência de 72 bpm e sem alterações de "
            "repolarização ventricular. Nenhuma evidência de isquemia aguda ou sobrecargas "
            "cavitárias."
        ),
    )

    service = ReportService(output_dir=output_dir)
    layout = service.generate_pdf(report, filename="sample_report.pdf")
    print(f"Laudo gerado em: {output_dir / 'sample_report.pdf'}")
    print(
        f"Marca: {layout.branding} | Responsabilidade técnica: {layout.technical_responsibility} "
        f"| Assinatura no rodapé: {layout.is_signature_in_footer}"
    )
