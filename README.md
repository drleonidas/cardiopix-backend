# cardiopix-backend

Plataforma CardioPix: Automação de laudos de ECG com inteligência artificial.

## Como executar

1. Instale dependências:
   ```bash
   npm install
   ```
2. Inicie o servidor (porta padrão 3000):
   ```bash
   npm start
   ```

O servidor expõe a página da clínica em `http://localhost:3000/clinica/dashboard` e as rotas de exames:
- `GET /exames` para listar envios.
- `POST /exames` para criar um novo exame com os campos `patientName` e `fileName`.

O armazenamento é mantido em memória para fins de demonstração.
