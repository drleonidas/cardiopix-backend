# cardiopix-backend

Plataforma CardioPix: Automação de laudos de ECG com inteligência artificial.

## Frontend estático

As páginas solicitadas estão em `frontend/medico`:

- `fila.html`: consome `GET /exames?status=aguardando` (ou dados mockados) e lista exames pendentes com o botão **Laudar**.
- `laudo.html`: formulário de laudo com campos técnicos e conclusão. O botão **Finalizar e Gerar PDF** envia `POST /exames/{id}/laudo`.

Para testar localmente com um servidor de arquivos simples:

```bash
cd frontend
python -m http.server 8000
```

Então abra no navegador:

- Fila: http://localhost:8000/medico/fila.html
- Laudo: http://localhost:8000/medico/laudo.html?id=123
