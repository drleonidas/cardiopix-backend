# cardiopix-backend

Plataforma CardioPix: Automação de laudos de ECG com inteligência artificial.

## Testes

Execute a suíte de integração com:

```bash
python -m pytest
```

## Gerar laudo de amostra

Use o script dedicado para gerar um PDF de texto com marca, responsabilidade técnica e assinatura:

```bash
python scripts/generate_sample_report.py
```

O arquivo é salvo em `reports/sample_report.pdf`.
