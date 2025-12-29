# cardiopix-backend

Plataforma CardioPix: Automação de laudos de ECG com inteligência artificial

## Relatórios (demo)

Este projeto inclui um serviço FastAPI simples para demonstrar a aba de relatórios com dados agregados de exames:

- Rota `/reports/aggregate` retorna faturamento (apenas laudos com status `Laudado`), contagem de exames (`Realizado`, `Pendente`, `Repetido`) e ranking de médicos por laudos emitidos, com filtros por período, clínica e médico, além de paginação do ranking.
- Interface `/reports` exibe cards, tabela e gráfico quantitativo consumindo essa rota.

### Executar localmente

1. Instale dependências:

   ```bash
   pip install -r requirements.txt
   ```

2. Inicie a API com recarregamento:

   ```bash
   uvicorn app.main:app --reload
   ```

3. Abra `http://localhost:8000/reports` para acessar a aba de relatórios.

Use os filtros para aplicar período (`start_date` e `end_date`), clínica (`clinic_id`) e médico (`doctor_id`). A paginação do ranking pode ser controlada pelos botões "Anterior" e "Próxima".
