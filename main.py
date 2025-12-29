from pathlib import Path
from typing import List
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile, status

from models import Clinica, Medico, Paciente

app = FastAPI(title="CardioPix Backend")

clinicas: List[Clinica] = []
medicos: List[Medico] = []
pacientes: List[Paciente] = []

base_dir = Path(__file__).resolve().parent
uploads_dir = base_dir / "uploads"
uploads_dir.mkdir(parents=True, exist_ok=True)


@app.get("/")
async def root():
    return {"message": "CardioPix API ativa"}


@app.post("/clinicas", response_model=Clinica, status_code=status.HTTP_201_CREATED)
async def cadastrar_clinica(clinica: Clinica):
    if any(item.cnpj == clinica.cnpj for item in clinicas):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CNPJ já cadastrado")
    clinicas.append(clinica)
    return clinica


@app.post("/medicos", response_model=Medico, status_code=status.HTTP_201_CREATED)
async def cadastrar_medico(medico: Medico):
    if any(item.crm == medico.crm for item in medicos):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CRM já cadastrado")
    if medico.clinica_id and not any(c.id == medico.clinica_id for c in clinicas):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clínica não encontrada")
    medicos.append(medico)
    return medico


@app.post("/pacientes", response_model=Paciente, status_code=status.HTTP_201_CREATED)
async def cadastrar_paciente(paciente: Paciente):
    if any(item.cpf == paciente.cpf for item in pacientes):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CPF já cadastrado")
    if paciente.clinica_id and not any(c.id == paciente.clinica_id for c in clinicas):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clínica não encontrada")
    pacientes.append(paciente)
    return paciente


@app.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_arquivo(arquivo: UploadFile = File(...)):
    if not arquivo.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nome de arquivo ausente")

    extensao = Path(arquivo.filename).suffix
    nome_final = f"{uuid4().hex}{extensao}"
    destino = uploads_dir / nome_final

    conteudo = await arquivo.read()
    destino.write_bytes(conteudo)

    return {
        "arquivo_original": arquivo.filename,
        "arquivo_salvo": nome_final,
        "caminho": str(destino.resolve()),
        "tamanho_bytes": len(conteudo),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
