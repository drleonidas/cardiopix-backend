# cardiopix-backend

Plataforma CardioPix: Automação de laudos de ECG com inteligência artificial.

## Sobre este protótipo

Este repositório contém um protótipo mínimo para geração do laudo técnico de ECG
em PDF. A aplicação Flask renderiza um template HTML com cabeçalho, dados do
médico (CRM/RQE), campos técnicos (RITMO, QRS, ST/T e CONCLUSÃO) e assinatura
no rodapé. Um botão na tela de exame aciona a geração do PDF via WeasyPrint.

## Execução local

1. Crie um ambiente virtual e instale as dependências:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Suba o servidor Flask:

   ```bash
   python app.py
   ```

3. Acesse http://localhost:8000/exame para visualizar o exame e use o botão
   **Gerar PDF** para abrir o laudo pronto para impressão.
