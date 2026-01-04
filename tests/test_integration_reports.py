from pathlib import Path

from cardiopix import (
    BillingOption,
    Clinic,
    Doctor,
    HealthUnitRegistration,
    PatientSession,
    PaymentError,
    PaymentMethod,
    PaymentService,
    PaymentStatus,
    ReportRequest,
    ReportService,
)


def read_report_text(pdf_path: Path) -> str:
    return pdf_path.read_text(encoding="utf-8")


def test_patient_pdf_requires_pix_payment(tmp_path: Path) -> None:
    clinic = Clinic(
        name="Clínica Solar",
        brand="CardioPix | Clínica Solar",
        technical_manager="Dra. Ana Lima",
        technical_id="CRM 0001",
    )
    doctor = Doctor(name="Dr. Breno Costa", registry="0002")
    session = PatientSession("Maria da Silva", payment_method=PaymentMethod.PIX)
    payments = PaymentService()

    service = ReportService(tmp_path)
    request = ReportRequest(
        clinic=clinic,
        doctor=doctor,
        patient_name=session.patient_name,
        findings="Ritmo sinusal com repolarização normal.",
    )

    try:
        payments.ensure_release_allowed(session)
        assert False, "Release should not be allowed before payment"
    except PaymentError:
        pass

    payments.mark_paid(session)
    payments.ensure_release_allowed(session)

    layout = service.generate_pdf(request, filename="paid_patient.pdf")
    text = read_report_text(tmp_path / "paid_patient.pdf")

    assert layout.is_signature_in_footer is True
    assert "CardioPix | Clínica Solar" in text
    assert "Responsável técnico: Dra. Ana Lima - CRM 0001" in text
    assert "Assinado digitalmente por Dr. Breno Costa" in text


def test_health_unit_billing_options_and_branding(tmp_path: Path) -> None:
    clinic = Clinic(
        name="Unidade Horizonte",
        brand="CardioPix | Unidade Horizonte",
        technical_manager="Dr. Hugo Mendes",
        technical_id="CRM 0300",
    )
    registration = HealthUnitRegistration(clinic=clinic, billing_option=BillingOption.FATURADO)

    doctor = Doctor(name="Dra. Cecília Matos", registry="0456", brand="CardioPix by Médica")
    session = PatientSession(
        "João Oliveira", payment_method=PaymentMethod.PIX, payment_status=PaymentStatus.PAID
    )

    service = ReportService(tmp_path)
    request = ReportRequest(
        clinic=registration.clinic,
        doctor=doctor,
        patient_name=session.patient_name,
        findings="Eixo elétrico normal e ausência de sinais de sobrecarga.",
    )

    layout = service.generate_pdf(request, filename="health_unit.pdf")
    text = read_report_text(tmp_path / "health_unit.pdf")

    assert registration.billing_option == BillingOption.FATURADO
    assert layout.branding == "CardioPix by Médica"
    assert layout.technical_responsibility.endswith("CRM 0300")
    assert "CardioPix by Médica" in text
    assert "Responsável técnico: Dr. Hugo Mendes - CRM 0300" in text
    assert layout.signature_y > (layout.page_height - 120)
