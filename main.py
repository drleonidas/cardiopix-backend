from datetime import datetime
from pathlib import Path
from typing import List, Dict

from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = Path("uploads")
app.config["UPLOAD_FOLDER"].mkdir(parents=True, exist_ok=True)

exames: List[Dict[str, str]] = [
    {
        "id": "001",
        "paciente": "João Silva",
        "tipo": "ECG",
        "status": "PENDENTE",
        "solicitado_em": datetime(2024, 5, 14, 10, 30),
    },
    {
        "id": "002",
        "paciente": "Maria Souza",
        "tipo": "ECG",
        "status": "LAUDADO",
        "solicitado_em": datetime(2024, 5, 13, 9, 15),
    },
    {
        "id": "003",
        "paciente": "Carlos Pereira",
        "tipo": "ECG",
        "status": "PENDENTE",
        "solicitado_em": datetime(2024, 5, 14, 14, 45),
    },
]

perfil_medico: Dict[str, str] = {
    "nome": "",
    "crm_uf": "",
    "rqe": "",
    "foto_perfil": "",
    "comprovante_crm": "",
}


def exames_pendentes() -> List[Dict[str, str]]:
    return [exame for exame in exames if exame.get("status") == "PENDENTE"]


@app.route("/dashboard_medico")
def dashboard_medico():
    pendentes = exames_pendentes()
    return render_template("dashboard_medico.html", exames=pendentes)


@app.route("/perfil_medico", methods=["GET", "POST"])
def perfil_medico_view():
    if request.method == "POST":
        perfil_medico["nome"] = request.form.get("nome", "").strip()
        perfil_medico["crm_uf"] = request.form.get("crm_uf", "").strip()
        perfil_medico["rqe"] = request.form.get("rqe", "").strip()

        foto_perfil = request.files.get("foto_perfil")
        comprovante_crm = request.files.get("comprovante_crm")

        if foto_perfil and foto_perfil.filename:
            caminho = app.config["UPLOAD_FOLDER"] / foto_perfil.filename
            foto_perfil.save(caminho)
            perfil_medico["foto_perfil"] = str(caminho)

        if comprovante_crm and comprovante_crm.filename:
            caminho = app.config["UPLOAD_FOLDER"] / comprovante_crm.filename
            comprovante_crm.save(caminho)
            perfil_medico["comprovante_crm"] = str(caminho)

        return redirect(url_for("perfil_medico_view"))

    return render_template("perfil_medico.html", perfil=perfil_medico)


@app.route("/exames/pendentes")
def listar_exames_pendentes():
    pendentes = exames_pendentes()
    return {"exames": pendentes}


if __name__ == "__main__":
    app.run(debug=True)
