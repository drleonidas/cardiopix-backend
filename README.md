# cardiopix-backend

Plataforma CardioPix: Automação de laudos de ECG com inteligência artificial

## Visão geral
Este backend demonstra o fluxo básico solicitado:
- Login com diferenciação de perfis (ADMIN/CLÍNICA e MÉDICO).
- Cadastro de exame pela clínica.
- Fila de laudos para o médico.
- Finalização do laudo com geração de PDF contendo cabeçalho, dados do paciente/médico, descrição técnica e conclusão.
- Endpoint para servir o PDF, permitindo abertura imediata em nova aba.

Os dados são mantidos em memória para facilitar testes manuais e o PDF é salvo em `data/pdfs/`.

## Pré-requisitos
- Python 3.11+

## Instalação
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Executando a API
```bash
uvicorn main:app --reload
```
A API ficará disponível em `http://localhost:8000`. A documentação automática (Swagger) pode ser acessada em `http://localhost:8000/docs`.

## Fluxo de teste sugerido
1. **Login**
   - `POST /login` com `{ "email": "clinica@teste.com", "password": "123", "role": "ADMIN/CLÍNICA" }` ou role `"MÉDICO"`.
2. **Cadastro de exame (clínica)**
   - `POST /exams` com `{ "patient_name": "Paciente Teste", "ecg_filename": "ecg_teste.pdf" }`.
3. **Fila de laudos (médico)**
   - `GET /exams/queue` para listar exames aguardando laudo.
4. **Finalizar e gerar PDF**
   - `POST /exams/{id}/report` com dados do médico, campos técnicos e conclusão. A resposta traz `pdf_url` (ex.: `/pdfs/exam-1.pdf`).
5. **Visualização imediata**
   - Abrir o `pdf_url` retornado em nova aba para conferir a formatação.

## Estrutura básica
- `main.py`: define a API FastAPI, modelos Pydantic, armazenamento em memória e geração de PDF com ReportLab.
- `data/pdfs/`: diretório onde os PDFs gerados são armazenados.
