# cardiopix-backend

Plataforma CardioPix: Automação de laudos de ECG com inteligência artificial.

## Executando

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Fluxo de laudo "Laudado"
- Endpoint `POST /reports/{report_id}/complete` marca o laudo como **laudado**.
- A transição atualiza o status do relatório e cria um evento `Laudado` com timestamp.
- O serviço de notificações dispara broadcast via WebSocket (`/ws`) com payload contendo destinatário, assunto e ID do laudo.
- O dashboard pode consumir o WebSocket para alternar visualmente o estado de Pendente (vermelho) para Laudado (verde); o endpoint `GET /reports` permite polling como alternativa.
