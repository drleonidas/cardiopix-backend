import os
from io import BytesIO
from typing import Dict, List

from flask import (Flask, redirect, render_template, request, send_file,
                   session, url_for)
from xhtml2pdf import pisa


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "cardiopix-secret-key")

    technical_defaults: List[Dict[str, str]] = [
        {"label": "Velocidade (mm/s)", "name": "velocidade", "placeholder": "25"},
        {"label": "Amplitude (mm/mV)", "name": "amplitude", "placeholder": "10"},
        {"label": "Derivações", "name": "derivacoes", "placeholder": "D1, D2, D3, aVR, aVL, aVF, V1-V6"},
        {"label": "Observações técnicas", "name": "observacoes", "placeholder": "Eletrodos posicionados em ..."},
    ]

    def require_login():
        if not session.get("medico_nome"):
            return False
        return True

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            session["medico_nome"] = request.form.get("medico_nome", "").strip()
            session["crm"] = request.form.get("crm", "").strip()
            session["rqe"] = request.form.get("rqe", "").strip()
            session["unidade_nome"] = request.form.get("unidade_nome", "").strip()
            session["unidade_logo"] = request.form.get("unidade_logo", "").strip()
            return redirect(url_for("laudo"))

        return render_template(
            "laudo.html",
            mode="login",
        )

    @app.route("/")
    def index():
        if not require_login():
            return redirect(url_for("login"))
        return redirect(url_for("laudo"))

    @app.route("/laudo", methods=["GET"])
    def laudo():
        if not require_login():
            return redirect(url_for("login"))

        initial_values = {item["name"]: request.args.get(item["name"], "") for item in technical_defaults}
        context = {
            "mode": "form",
            "technical_defaults": technical_defaults,
            "technical_values": initial_values,
            "ritmo": request.args.get("ritmo", ""),
            "qrs": request.args.get("qrs", ""),
            "st_t": request.args.get("st_t", ""),
            "conclusao": request.args.get("conclusao", ""),
        }
        return render_template("laudo.html", **context)

    @app.route("/generate-pdf", methods=["POST"])
    def generate_pdf():
        if not require_login():
            return redirect(url_for("login"))

        technical_values = {item["name"]: request.form.get(item["name"], "") for item in technical_defaults}
        ritmo = request.form.get("ritmo", "")
        qrs = request.form.get("qrs", "")
        st_t = request.form.get("st_t", "")
        conclusao = request.form.get("conclusao", "")
        assinatura = request.form.get("assinatura", "")

        html = render_template(
            "laudo.html",
            mode="pdf",
            technical_defaults=technical_defaults,
            technical_values=technical_values,
            ritmo=ritmo,
            qrs=qrs,
            st_t=st_t,
            conclusao=conclusao,
            assinatura=assinatura,
        )

        pdf_bytes = BytesIO()
        pisa.CreatePDF(html, dest=pdf_bytes)
        pdf_bytes.seek(0)

        filename = "laudo-ecg.pdf"
        return send_file(
            pdf_bytes,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=filename,
        )

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
