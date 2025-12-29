# cardiopix-backend

Plataforma CardioPix: Automação de laudos de ECG com inteligência artificial.

## Endpoints

### Finalizar laudo e gerar PDF

**POST** `/reports/{report_id}/finalize`

Corpo JSON:

```json
{
  "patient_name": "Maria Silva",
  "report_summary": "Sinusal, sem alterações agudas",
  "clinician_name": "Dr. Souza"
}
```

Resposta:

```json
{
  "status": "finalized",
  "pdfUrl": "/reports/123/pdf",
  "pdfPath": "storage/pdfs/123.pdf"
}
```

### Obter o PDF

**GET** `/reports/{report_id}/pdf`

Retorna o arquivo com `Content-Type: application/pdf` e `Content-Disposition: inline` para abertura direta no navegador.

## Execução local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Após finalizar, abra a URL retornada em nova aba (`window.open(pdfUrl, '_blank')`) para conferência imediata.
