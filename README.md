# cardiopix-backend

Plataforma CardioPix: Automação de laudos de ECG com inteligência artificial.

## Notificações de conclusão de exame

Este serviço expõe um endpoint que mapeia a assinatura/conclusão de um exame, gera o PDF do laudo e dispara notificações pelos canais cadastrados do paciente (WhatsApp e e-mail).

### Executando localmente

1. Instale dependências: `pip install -r requirements.txt`.
2. Suba a API: `uvicorn app.main:app --reload`.
3. Envie um evento de conclusão de exame:

```bash
curl -X POST http://localhost:8000/events/exams/completed \
  -H "Content-Type: application/json" \
  -d '{
    "exam_id": "exam-123",
    "report_summary": "ECG sem alterações relevantes",
    "patient": {
      "name": "Paciente Teste",
      "email": "paciente@example.com",
      "whatsapp": "+5511999999999"
    }
  }'
```

O serviço gera um PDF em `data/reports/` e registra logs de entrega em `/delivery-logs`.

### Configuração de provedores

Defina as variáveis no `.env` conforme o provedor desejado:

- **WhatsApp**: `whatsapp_provider=twilio` ou `360dialog` (+ credenciais específicas).
- **E-mail**: `email_provider=sendgrid` ou `ses` (+ credenciais específicas).
- `max_delivery_attempts` e `retry_backoff_seconds` controlam retries e backoff.
