"""Motor de geração de sugestões de laudo de ECG."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.normas_sbc import NORMAS_SBC_2022, avaliar_parametro


def calcular_imc(peso: Optional[float], altura: Optional[float]) -> Optional[float]:
    """Retorna o IMC arredondado com uma casa decimal."""
    if not peso or not altura:
        return None
    try:
        return round(float(peso) / (float(altura) ** 2), 1)
    except (ZeroDivisionError, ValueError, TypeError):
        return None


def _avaliar_rv5_sv1(rv5: Optional[float], sv1: Optional[float]) -> Optional[float]:
    if rv5 is None or sv1 is None:
        return None
    try:
        return float(rv5) + float(sv1)
    except (ValueError, TypeError):
        return None


def gerar_sugestao_laudo(exame: Dict[str, Any]) -> Dict[str, Any]:
    """Produz um rascunho de laudo a partir de dados clínicos e do traçado."""

    sexo = exame.get("sexo")
    imc = calcular_imc(exame.get("peso"), exame.get("altura"))
    rv5_sv1 = _avaliar_rv5_sv1(exame.get("rv5"), exame.get("sv1"))

    fc_info = avaliar_parametro("FC", exame.get("fc"), sexo)
    pr_info = avaliar_parametro("PR", exame.get("pr"), sexo)
    qrs_info = avaliar_parametro("QRS", exame.get("qrs"), sexo)
    qtc_info = avaliar_parametro("QTc", exame.get("qtc"), sexo)

    alertas: List[str] = []
    if any(info.get("status") == "limite" for info in (fc_info, pr_info, qrs_info, qtc_info)):
        alertas.append("Atenção: Parâmetros limítrofes conforme SBC 2022")
    if any(info.get("status") == "indisponivel" for info in (fc_info, pr_info, qrs_info, qtc_info)):
        alertas.append("Parâmetros incompletos para avaliação integral do traçado")

    ritmo = _descrever_ritmo(exame.get("fc"), exame.get("ritmo"), fc_info)
    onda_p = _descrever_onda_p(exame, pr_info)
    qrs_texto = _descrever_qrs(exame, qrs_info, rv5_sv1)
    st_t = exame.get("st_t") or "Sem alterações significativas de ST/T"
    qt_qtc = _descrever_qt(qtc_info, exame.get("qt"), exame.get("qtc"))

    conclusoes = _construir_conclusao(imc, rv5_sv1, qrs_info, qtc_info, st_t, sexo, exame.get("idade"))
    conclusao_texto = "; ".join(conclusoes) if conclusoes else "Traçado dentro dos padrões de normalidade"

    return {
        "imc": imc,
        "alertas": alertas,
        "sugestoes": {
            "RITMO": ritmo,
            "ONDA P": onda_p,
            "QRS": qrs_texto,
            "ST/T": st_t,
            "QT/QTc": qt_qtc,
            "CONCLUSAO": conclusao_texto,
        },
        "referencias": {chave: norma.unidade for chave, norma in NORMAS_SBC_2022.items()},
    }


def _descrever_ritmo(fc: Optional[float], ritmo: Optional[str], fc_info: Dict[str, str]) -> str:
    if ritmo:
        return ritmo
    if fc is None:
        return "Ritmo não determinado (FC ausente)"
    if fc < 60:
        return f"Bradicardia sinusal ({fc} bpm)"
    if fc > 100:
        return f"Taquicardia sinusal ({fc} bpm)"
    if fc_info.get("status") == "limite":
        return f"Ritmo sinusal em faixa limítrofe ({fc} bpm)"
    return f"Ritmo sinusal ({fc} bpm)"


def _descrever_onda_p(exame: Dict[str, Any], pr_info: Dict[str, str]) -> str:
    eixo_p = exame.get("eixo_p")
    onda_p_duracao = exame.get("onda_p")
    partes = []
    if onda_p_duracao:
        partes.append(f"Duração da onda P: {onda_p_duracao} ms")
    if eixo_p is not None:
        partes.append(f"Eixo de P: {eixo_p}º")
    if pr_info.get("status") == "alterado":
        partes.append("PR fora da faixa de normalidade")
    elif pr_info.get("status") == "limite":
        partes.append("PR em faixa limítrofe")
    if not partes:
        return "Ondas P sem observações adicionais"
    return "; ".join(partes)


def _descrever_qrs(exame: Dict[str, Any], qrs_info: Dict[str, str], rv5_sv1: Optional[float]) -> str:
    eixo_qrs = exame.get("eixo_qrs")
    partes = []
    duracao_qrs = exame.get("qrs")
    if duracao_qrs:
        partes.append(f"Duração do QRS: {duracao_qrs} ms")
    if eixo_qrs is not None:
        partes.append(f"Eixo de QRS: {eixo_qrs}º")
    if qrs_info.get("status") == "alterado":
        partes.append("QRS alargado - avaliar bloqueios de ramo")
    elif qrs_info.get("status") == "limite":
        partes.append("QRS em faixa limítrofe")
    if rv5_sv1 is not None:
        partes.append(f"RV5 + SV1 = {rv5_sv1} mm")
        if rv5_sv1 > 35:
            partes.append("Índice de Sokolow-Lyon elevado")
    if not partes:
        return "QRS sem observações adicionais"
    return "; ".join(partes)


def _descrever_qt(qtc_info: Dict[str, str], qt: Optional[float], qtc: Optional[float]) -> str:
    partes = []
    if qt:
        partes.append(f"QT: {qt} ms")
    if qtc:
        partes.append(f"QTc: {qtc} ms")
    status = qtc_info.get("status")
    if status == "alterado":
        partes.append("QTc prolongado")
    elif status == "limite":
        partes.append("QTc em faixa limítrofe")
    if not partes:
        return "Sem alterações relevantes de QT/QTc"
    return "; ".join(partes)


def _construir_conclusao(
    imc: Optional[float],
    rv5_sv1: Optional[float],
    qrs_info: Dict[str, str],
    qtc_info: Dict[str, str],
    st_t: str,
    sexo: Optional[str],
    idade: Optional[int],
) -> List[str]:
    conclusoes: List[str] = []
    if imc and imc >= 30:
        complemento = f" em paciente {idade} anos" if idade else ""
        sexo_descr = f" ({sexo})" if sexo else ""
        conclusoes.append(f"IMC {imc} kg/m²{complemento}{sexo_descr} - Possível Sobrecarga Ventricular")
    if rv5_sv1 is not None and rv5_sv1 > 35:
        conclusoes.append("Critério de hipertrofia ventricular esquerda (Sokolow-Lyon)")
    if qrs_info.get("status") == "alterado":
        conclusoes.append("QRS alargado - investigar bloqueio de ramo")
    if qtc_info.get("status") == "alterado":
        conclusoes.append("QTc prolongado - risco de instabilidade elétrica")
    if "depress" in st_t.lower() or "elevação" in st_t.lower():
        conclusoes.append("Alterações de ST/T requerem correlação clínica")
    return conclusoes
