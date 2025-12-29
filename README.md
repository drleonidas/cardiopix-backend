# cardiopix-backend

Plataforma CardioPix: Automação de laudos de ECG com inteligência artificial.

## Assinatura digital de laudos

O backend agora inclui um serviço de orquestração de assinatura digital ICP-Brasil para laudos médicos. O fluxo principal é:

1. Gerar o PDF contendo os dados do médico, da clínica e do laudo.
2. Enviar o PDF para o serviço de assinatura usando o certificado do médico (via `SignerClient`).
3. Atualizar o status do laudo para pendente enquanto a assinatura é processada.
4. Processar callbacks de sucesso/erro para marcar o laudo como assinado ou com falha, preservando o PDF assinado quando disponível.

### Executando testes

Use o runner de testes da biblioteca padrão:

```bash
python -m unittest discover
```
