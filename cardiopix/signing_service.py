from __future__ import annotations

from .models import Laudo, LaudoStatus, SignatureCallback
from .pdf_generator import PDFGenerator
from .repository import InMemoryLaudoRepository
from .signer_client import SignerClient


class SigningService:
    def __init__(
        self,
        repository: InMemoryLaudoRepository,
        signer_client: SignerClient,
        pdf_generator: PDFGenerator,
    ) -> None:
        self.repository = repository
        self.signer_client = signer_client
        self.pdf_generator = pdf_generator

    def finalize_and_request_signature(self, laudo_id: str) -> str:
        laudo = self.repository.get(laudo_id)
        if laudo is None:
            raise KeyError(f"Laudo {laudo_id} not found")

        laudo.pdf_bytes = self.pdf_generator.generate(laudo)
        request = self.signer_client.request_signature(
            pdf_bytes=laudo.pdf_bytes,
            physician=laudo.physician,
            clinic=laudo.clinic,
            laudo=laudo,
        )
        laudo.status = LaudoStatus.PENDING_SIGNATURE
        laudo.signature_request_id = request.id
        self.repository.update(laudo)
        return request.id

    def handle_signing_callback(self, callback: SignatureCallback) -> None:
        laudo = self._find_laudo_by_request(callback.request_id)
        if laudo is None:
            raise KeyError(f"Signature request {callback.request_id} not mapped to any laudo")

        if callback.succeeded:
            laudo.status = LaudoStatus.SIGNED
            laudo.signed_pdf_bytes = callback.signed_pdf_bytes
            laudo.failure_reason = None
        else:
            laudo.status = LaudoStatus.SIGNATURE_FAILED
            laudo.failure_reason = callback.error_message or "Signature failed"
        self.repository.update(laudo)

    def _find_laudo_by_request(self, request_id: str) -> Laudo:
        for laudo in self.repository._laudos.values():
            if laudo.signature_request_id == request_id:
                return laudo
        raise KeyError(f"Signature request {request_id} not found")
