# cardiopix-backend

Plataforma CardioPix: Automação de laudos de ECG com inteligência artificial

## Execução

Instale as dependências e inicie o servidor FastAPI:

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## Fluxo de autenticação

- `POST /login`: recebe `username` e `password` e identifica se é Clínica, Médico ou Paciente.
- Cada perfil recebe um `token` e a rota do respectivo painel (`/dashboard/clinica`, `/dashboard/medico`, `/dashboard/paciente`).
- As rotas de dashboard exigem o token no cabeçalho `Authorization: Bearer <token>` e retornam erro 403 quando acessadas por outro perfil.
- `DELETE /logout`: encerra a sessão invalidando o token.
