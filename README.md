# cardiopix-backend

Plataforma CardioPix: Automação de laudos de ECG com inteligência artificial

## Produtividade por médico

Este repositório inclui utilitários para calcular produtividade de médicos com base em laudos concluídos em um período. O módulo `src/productivity/aggregator.py` oferece funções para:

* **Agrupar laudos concluídos por médico** com filtros de intervalo de datas.
* **Calcular métricas de painel** como total de laudos, valor bruto, ticket médio e valor associado a uma política de pagamentos.
* **Ordenar rankings** de produtividade conforme métricas escolhidas.
* **Exportar para CSV** para integrar com a seção de Produtividade ou fazer auditoria offline.

### Exemplo rápido

```python
from datetime import date
from src.productivity.aggregator import PaymentPolicy, aggregate_by_doctor
from src.productivity.export import export_ranking

reports = [
    {"doctor_id": "d1", "status": "concluido", "value": 120.0, "created_at": "2024-05-01"},
    {"doctor_id": "d2", "status": "concluido", "value": 90.0, "created_at": "2024-05-02"},
    {"doctor_id": "d1", "status": "concluido", "value": 130.0, "created_at": "2024-05-03"},
]

policy = PaymentPolicy(percentage=0.1, fixed_bonus=5)
metrics = aggregate_by_doctor(reports, date(2024, 5, 1), date(2024, 5, 31), payment_policy=policy)
export_ranking(metrics, order_by="payable_total", destination="ranking_maio.csv")
```

O resultado `ranking_maio.csv` trará o ranking ordenado pela métrica escolhida e pronto para ser exibido no painel ou compartilhado.
