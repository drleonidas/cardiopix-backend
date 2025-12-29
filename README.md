# cardiopix-backend
Plataforma CardioPix: Automação de laudos de ECG com inteligência artificial

## Serviço de PDF de Laudos

O diretório `services/pdf` contém utilitários para gerar laudos médicos em PDF a partir de um template HTML.

### Requisitos

Instale as dependências necessárias (ex.: em um ambiente virtual):

```bash
pip install -r requirements.txt
```

### Uso

```python
from services.pdf.laudo import DoctorData, ExamData, PatientData, generate_laudo_pdf

paciente = PatientData(
    nome="Maria da Silva",
    data_nascimento="1985-07-12",
    sexo="Feminino",
    identificador="123456"
)

medico = DoctorData(
    nome="Dr. João Souza",
    crm="12345-SP",
    especialidade="Cardiologia"
)

exame = ExamData(
    descricao_tecnica="ECG de 12 derivações realizado em repouso.",
    conclusao="Traçado dentro dos limites da normalidade.",
    data_exame="2024-03-10",
    protocolo="PROTO-001"
)

pdf_bytes = generate_laudo_pdf(paciente=paciente, medico=medico, exame=exame)
with open("laudo.pdf", "wb") as fp:
    fp.write(pdf_bytes)
```

O template padrão inclui cabeçalho com logotipo placeholder, blocos de dados do paciente e do médico laudador, além de áreas dedicadas à descrição técnica e conclusão do exame.
