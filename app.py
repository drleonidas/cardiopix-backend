from datetime import datetime
from io import BytesIO

from flask import Flask, render_template, request, send_file, url_for
from weasyprint import HTML

app = Flask(__name__)


def build_exam_context():
    """Return the mock exam data used to render the laudo."""
    exam_date = datetime.now()
    return {
        "unit_name": "Unidade CardioPix",
        "doctor": {
            "name": "Dra. Ana Silva",
            "crm": "CRM 123456",
            "rqe": "RQE 7890",
        },
        "patient_name": "João Souza",
        "ritmo": "Ritmo sinusal regular",
        "qrs": "QRS estreito, duração aproximada de 90 ms",
        "stt": "ST/T sem alterações isquêmicas dinâmicas",
        "conclusao": "Eletrocardiograma dentro da normalidade para a faixa etária.",
        "exam_date": exam_date,
        "formatted_date": exam_date.strftime("%d/%m/%Y %H:%M"),
    }


@app.route("/exame")
def exame():
    exam = build_exam_context()
    return render_template("exame.html", exam=exam)


@app.route("/laudo")
def laudo():
    exam = build_exam_context()
    return render_template("laudo.html", exam=exam)


@app.route("/laudo/pdf")
def laudo_pdf():
    exam = build_exam_context()
    html = render_template("laudo.html", exam=exam, pdf_mode=True)
    pdf_bytes = HTML(string=html, base_url=request.host_url).write_pdf()
    return send_file(
        BytesIO(pdf_bytes),
        download_name="laudo.pdf",
        mimetype="application/pdf",
    )


@app.route("/")
def root_redirect():
    return render_template("exame.html", exam=build_exam_context())


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
