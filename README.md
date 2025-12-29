# cardiopix-backend
Plataforma CardioPix: Automação de laudos de ECG com inteligência artificial

## Digital signing flow

This repository contains a minimal workflow to persist laudo records, capture
signing metadata, and render PDF outputs with the physician's signature.

1. Provide a digital signing response containing an ISO8601 timestamp and a
   base64-encoded PNG signature.
2. Call `create_signed_laudo` with the laudo content, physician data, and the
   signing response. The laudo is persisted to `data/laudos.json` with the
   signing timestamp and stored signature path.
3. A PDF is generated in `data/pdfs/` placing the physician signature image
   above the CRM/RQE block and printing the signing timestamp for auditability.

### Running the example

```bash
pip install -r requirements.txt
python app.py
```

Replace the placeholder `signature_image` value in `app.py` with the base64
payload returned by the signing provider to embed the actual signature image.
