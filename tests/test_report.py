import pytest

from cardiopix.report import LaudoPayloadBuilder, PhysicianIdentifiersMissing, Responsibility


def test_responsibility_extraction_and_payload_mapping():
    session = {
        "physician_name": "Dr. Ana Silva",
        "physician_crm": "12345",
        "physician_crm_uf": "SP",
        "physician_rqe": "9876",
    }
    base_payload = {"exam_id": "ecg-1", "patient_id": "pat-1"}

    builder = LaudoPayloadBuilder(session)
    payload = builder.build(base_payload)

    assert payload["exam_id"] == "ecg-1"
    assert payload["patient_id"] == "pat-1"
    assert payload["physician_name"] == "Dr. Ana Silva"
    assert payload["physician_crm"] == "12345"
    assert payload["physician_crm_uf"] == "SP"
    assert payload["physician_rqe"] == "9876"
    assert "responsibility" in payload
    assert payload["responsibility"].startswith("Dr(a). Dr. Ana Silva - CRM 12345/SP - RQE 9876")
    assert payload["responsibility_section"]["physician_crm"] == "12345"


def test_missing_identifiers_raise_error():
    session = {
        "physician_name": "Dr. Ana Silva",
        "physician_crm": "",
        "physician_crm_uf": "SP",
        "physician_rqe": "",
    }
    builder = LaudoPayloadBuilder(session)

    with pytest.raises(PhysicianIdentifiersMissing) as excinfo:
        builder.build({})

    assert set(excinfo.value.missing_fields) == {"CRM", "RQE"}


def test_responsibility_from_session_requires_identifiers():
    session = {"physician_name": "", "physician_crm": "", "physician_crm_uf": "", "physician_rqe": ""}
    with pytest.raises(PhysicianIdentifiersMissing):
        Responsibility.from_session(session)
