# cardiopix-backend

Plataforma CardioPix: Automação de laudos de ECG com inteligência artificial

## Auditoria de laudos

Este serviço FastAPI adiciona trilha de auditoria para visualização e envio de laudos.

### Execução local
1. Crie ambiente virtual e instale dependências:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Defina variáveis sensíveis (opcional):
   ```bash
   export COMPLIANCE_TOKEN="token-de-compliance"
   export AUDIT_SALT="sal-unico"
   export DATABASE_URL="sqlite:///./data/app.db"
   ```
3. Inicie o servidor:
   ```bash
   uvicorn app.main:app --reload
   ```

### Endpoints
- `GET /reports/{report_id}/pdf` — exige header `x-user-id`; registra ação `viewed`.
- `POST /reports/{report_id}/send` — exige header `x-user-id` e body `{ "channel": "email", "message": "..." }`; registra ação `sent`.
- `GET /compliance/audit-logs` — protegido por header `x-compliance-token`; aceita filtros `x-user-id`, `action`, `channel`, `report_id`, `start`, `end`, `page`, `page_size`.

Identificadores de usuário são salvos apenas na forma de hash salgado (`hashed_user_id`) e com referência curta (`user_reference`) para minimizar exposição conforme LGPD.
