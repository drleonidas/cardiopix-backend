import io
import logging
import os
import re
from pathlib import Path
from typing import Dict, Optional, Tuple

from flask import Flask, Response, flash, redirect, render_template, request, url_for
from PIL import Image

try:
    import pytesseract
except Exception:  # pragma: no cover - optional dependency may be missing at runtime
    pytesseract = None


LOG_PATH = Path("logs/seguranca_validacao.log")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("validacao_crm")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S"
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


app = Flask(__name__, template_folder=".")
app.secret_key = os.environ.get("APP_SECRET_KEY", "cardiopix-secret-key")

MEDICO_ESTADO: Dict[str, str] = {
    "nome_digitado": "",
    "crm_digitado": "",
    "nome_documento": "",
    "crm_documento": "",
    "status": "PENDENTE",
    "pode_assinar": "nao",
    "detalhes_validacao": "Nenhuma análise realizada ainda.",
}


def _normalizar_nome(valor: str) -> str:
    return re.sub(r"\s+", " ", valor).strip().upper()


def _normalizar_crm(valor: str) -> str:
    return re.sub(r"\D", "", valor)


def extrair_texto_documento(arquivo) -> str:
    conteudo = arquivo.read()
    arquivo.seek(0)
    try:
        imagem = Image.open(io.BytesIO(conteudo))
    except Exception:
        try:
            return conteudo.decode("utf-8", errors="ignore")
        except Exception:
            return ""

    if pytesseract is None:
        return ""

    texto = pytesseract.image_to_string(imagem)
    return texto or ""


def detectar_campos_crm(texto: str) -> Tuple[Optional[str], Optional[str]]:
    linhas = [linha.strip() for linha in texto.splitlines() if linha.strip()]
    nome_documento = None
    crm_documento = None

    for linha in linhas:
        if not nome_documento and len(linha) > 5:
            if any(palavra in linha.upper() for palavra in ["CRM", "MED", "MEDICO", "DR", "DRA"]):
                partes = re.sub(r"CRM.*", "", linha, flags=re.IGNORECASE).strip()
                if partes:
                    nome_documento = partes
        if crm_documento is None:
            crm_match = re.search(r"CRM\s*[:#-]?\s*(\d+)", linha, flags=re.IGNORECASE)
            if crm_match:
                crm_documento = crm_match.group(1)
        if nome_documento and crm_documento:
            break

    if crm_documento is None:
        numeros = re.findall(r"\b\d{5,}\b", " ".join(linhas))
        if numeros:
            crm_documento = numeros[0]

    if nome_documento is None and linhas:
        nome_documento = linhas[0]

    return nome_documento, crm_documento


def validar_documento_crm(nome_digitado: str, crm_digitado: str, arquivo) -> Dict[str, str]:
    texto_documento = extrair_texto_documento(arquivo)
    nome_documento, crm_documento = detectar_campos_crm(texto_documento)

    nome_form_normalizado = _normalizar_nome(nome_digitado)
    nome_doc_normalizado = _normalizar_nome(nome_documento or "")

    crm_form_normalizado = _normalizar_crm(crm_digitado)
    crm_doc_normalizado = _normalizar_crm(crm_documento or "")

    nome_confere = bool(nome_doc_normalizado) and nome_doc_normalizado == nome_form_normalizado
    crm_confere = bool(crm_doc_normalizado) and crm_doc_normalizado == crm_form_normalizado

    aprovado = nome_confere and crm_confere
    status = "APROVADO" if aprovado else "AGUARDANDO VALIDACAO"
    pode_assinar = "sim" if aprovado else "nao"
    detalhes_validacao = (
        "Nome e CRM coincidem com o documento enviado."
        if aprovado
        else "Pendência: divergência entre dados digitados e o arquivo enviado."
    )

    resultado = {
        "nome_digitado": nome_digitado,
        "crm_digitado": crm_digitado,
        "nome_documento": nome_documento or "Não identificado",
        "crm_documento": crm_documento or "Não identificado",
        "status": status,
        "pode_assinar": pode_assinar,
        "detalhes_validacao": detalhes_validacao,
    }

    logger.info(
        "Validacao CRM - nome_form='%s' crm_form='%s' nome_doc='%s' crm_doc='%s' status='%s'",
        nome_digitado,
        crm_digitado,
        nome_documento or "",
        crm_documento or "",
        status,
    )

    return resultado


@app.route("/perfil-medico", methods=["GET", "POST"])
def perfil_medico() -> Response:
    if request.method == "POST":
        nome = request.form.get("nome", "")
        crm = request.form.get("crm", "")
        arquivo = request.files.get("documento")

        if not arquivo or arquivo.filename == "":
            flash("Envie um arquivo do CRM para validação automática.", "error")
            return redirect(url_for("perfil_medico"))

        resultado = validar_documento_crm(nome, crm, arquivo)
        MEDICO_ESTADO.update(resultado)
        flash(
            "Dados validados automaticamente. Status atual: %s." % resultado["status"],
            "success",
        )

    return render_template(
        "perfil_medico.html",
        nome=MEDICO_ESTADO.get("nome_digitado", ""),
        crm=MEDICO_ESTADO.get("crm_digitado", ""),
        status=MEDICO_ESTADO.get("status", "PENDENTE"),
        pode_assinar=MEDICO_ESTADO.get("pode_assinar", "nao"),
        nome_documento=MEDICO_ESTADO.get("nome_documento", ""),
        crm_documento=MEDICO_ESTADO.get("crm_documento", ""),
        detalhes_validacao=MEDICO_ESTADO.get("detalhes_validacao", ""),
    )


@app.route("/assinar-laudo", methods=["POST"])
def assinar_laudo() -> Response:
    if MEDICO_ESTADO.get("status") != "APROVADO":
        mensagem = (
            "Assinatura bloqueada: aguardando validação automática do documento CRM."
        )
        return mensagem, 403

    return "Laudo assinado com sucesso!", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=True)
