from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from flask import Flask, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).parent
UPLOAD_FOLDER = BASE_DIR / "static" / "logos"
PROFILE_STORE = BASE_DIR / "clinic_profile.json"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.secret_key = "cardiopix-secret-key"

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def load_profile() -> Dict[str, Optional[str]]:
    if PROFILE_STORE.exists():
        with PROFILE_STORE.open("r", encoding="utf-8") as profile_file:
            return json.load(profile_file)
    return {"razao_social": "", "cnpj": "", "endereco": "", "logo_filename": None}


def save_profile(profile: Dict[str, Optional[str]]) -> None:
    with PROFILE_STORE.open("w", encoding="utf-8") as profile_file:
        json.dump(profile, profile_file, ensure_ascii=False, indent=2)


def get_clinic_logo_path() -> Optional[Path]:
    """Return the path to the saved clinic logo for use in laudo headers."""
    profile = load_profile()
    logo_filename = profile.get("logo_filename")
    if not logo_filename:
        return None

    logo_path = UPLOAD_FOLDER / logo_filename
    return logo_path if logo_path.exists() else None


@app.route("/perfil_clinica", methods=["GET", "POST"])
def clinic_profile():
    profile = load_profile()

    if request.method == "POST":
        razao_social = request.form.get("razao_social", "").strip()
        cnpj = request.form.get("cnpj", "").strip()
        endereco = request.form.get("endereco", "").strip()
        logo_file = request.files.get("logo")

        if not razao_social or not cnpj or not endereco:
            flash("Preencha todos os campos obrigatórios.", "erro")
            return render_template("perfil_clinica.html", profile=profile)

        profile.update({
            "razao_social": razao_social,
            "cnpj": cnpj,
            "endereco": endereco,
        })

        if logo_file and logo_file.filename:
            if allowed_file(logo_file.filename):
                extension = logo_file.filename.rsplit(".", 1)[1].lower()
                filename = secure_filename(f"clinic_logo.{extension}")
                save_path = UPLOAD_FOLDER / filename
                logo_file.save(save_path)
                profile["logo_filename"] = filename
                flash("Dados e logomarca da clínica salvos com sucesso!", "sucesso")
            else:
                flash("Formato de arquivo não permitido. Use png, jpg, jpeg ou gif.", "erro")
                return render_template("perfil_clinica.html", profile=profile)
        else:
            flash("Dados da clínica atualizados.", "sucesso")

        save_profile(profile)
        return redirect(url_for("clinic_profile"))

    return render_template("perfil_clinica.html", profile=profile)


@app.route("/")
def index():
    return redirect(url_for("clinic_profile"))


if __name__ == "__main__":
    app.run(debug=True)
