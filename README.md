# cardiopix-backend

Plataforma CardioPix: Automação de laudos de ECG com inteligência artificial.

## Módulo Financeiro
- Função `build_payment_split` em `cardiopix_backend/finance.py` calcula o split Bruto - Taxas - Impostos 2026 - Repasse Médico, validando valores negativos e retornando o lucro líquido e o detalhamento da operação.

## Dashboard de BI
- `summarize_exams` em `cardiopix_backend/dashboard.py` consolida exames por mês, retornando volume e faturamento para alimentar gráficos de BI.

## Gatilho de Notificações
- `NotificationService` em `cardiopix_backend/notifications.py` dispara mensagens de WhatsApp e e-mail quando um exame muda para status `Laudado`.

## Executando os testes
```bash
python -m pytest
```
