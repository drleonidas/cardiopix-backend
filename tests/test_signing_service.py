import unittest

from cardiopix.models import Clinic, Laudo, Physician, SignatureCallback
from cardiopix.pdf_generator import PDFGenerator
from cardiopix.repository import InMemoryLaudoRepository
from cardiopix.signer_client import SignerClient
from cardiopix.signing_service import SigningService
from cardiopix.models import LaudoStatus


class SigningServiceTest(unittest.TestCase):
    def setUp(self):
        self.repository = InMemoryLaudoRepository()
        self.signer_client = SignerClient()
        self.pdf_generator = PDFGenerator()
        self.service = SigningService(self.repository, self.signer_client, self.pdf_generator)

        self.physician = Physician(id="med-1", name="Dr. Alice", certificate_path="/tmp/certs/alice.pfx")
        self.clinic = Clinic(id="clinic-9", name="CardioPix Clinic")
        self.laudo = Laudo(id="laudo-1", physician=self.physician, clinic=self.clinic, content="ECG normal")
        self.repository.add(self.laudo)

    def test_finalize_generates_pdf_and_requests_signature(self):
        request_id = self.service.finalize_and_request_signature(self.laudo.id)

        stored = self.repository.get(self.laudo.id)
        self.assertEqual(stored.status, LaudoStatus.PENDING_SIGNATURE)
        self.assertEqual(stored.signature_request_id, request_id)
        self.assertIsNotNone(stored.pdf_bytes)
        self.assertIn(self.physician.name, stored.pdf_bytes.decode())
        self.assertIn(self.clinic.name, stored.pdf_bytes.decode())

    def test_handle_success_callback_marks_laudo_signed(self):
        request_id = self.service.finalize_and_request_signature(self.laudo.id)
        signed_pdf = b"signed-pdf-content"
        callback = SignatureCallback(request_id=request_id, succeeded=True, signed_pdf_bytes=signed_pdf)

        self.service.handle_signing_callback(callback)

        stored = self.repository.get(self.laudo.id)
        self.assertEqual(stored.status, LaudoStatus.SIGNED)
        self.assertEqual(stored.signed_pdf_bytes, signed_pdf)
        self.assertIsNone(stored.failure_reason)

    def test_handle_failure_callback_marks_laudo_failed(self):
        request_id = self.service.finalize_and_request_signature(self.laudo.id)
        callback = SignatureCallback(request_id=request_id, succeeded=False, error_message="Invalid cert")

        self.service.handle_signing_callback(callback)

        stored = self.repository.get(self.laudo.id)
        self.assertEqual(stored.status, LaudoStatus.SIGNATURE_FAILED)
        self.assertEqual(stored.failure_reason, "Invalid cert")


if __name__ == "__main__":
    unittest.main()
