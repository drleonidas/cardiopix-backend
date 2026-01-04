# Cenários de teste manual

## Cenário 1: Clínica
1. Autenticar como usuário **ADMIN/CLÍNICA**.
2. Acessar a opção **Novo Exame**.
3. Selecionar um paciente de teste.
4. Anexar um arquivo simulado ao exame.
5. Salvar o exame.
6. Voltar para a lista de exames e confirmar que o novo registro aparece com o paciente e anexo exibidos.

## Cenário 2: Médico
1. Autenticar como usuário **MÉDICO**.
2. Navegar até **Fila de Laudos**.
3. Abrir um exame selecionando o paciente desejado.
4. Preencher os campos técnicos exigidos.
5. Inserir a conclusão do laudo.
6. Clicar em **Finalizar e Gerar PDF**.
7. Confirmar que o PDF abre em uma nova aba contendo cabeçalho, dados do paciente e do médico, descrição técnica e conclusão.
