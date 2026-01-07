"""Valores de referência da Diretriz Brasileira de 2022 (SBC) para eletrocardiograma.

Este módulo isola limites de parâmetros básicos e auxilia na classificação de
resultados como normais, limítrofes ou alterados.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class ReferenciaSBC2022:
    """Faixas ou limites de um parâmetro eletrocardiográfico."""

    minimo: Optional[float]
    maximo: Optional[float]
    unidade: str
    limites_por_sexo: Optional[Dict[str, float]] = None

    def limite_superior(self, sexo: Optional[str] = None) -> Optional[float]:
        if self.limites_por_sexo is None:
            return self.maximo

        if sexo:
            chave = sexo.lower()
            if chave in self.limites_por_sexo:
                return self.limites_por_sexo[chave]
        # Retorna o limite mais conservador quando não informado
        return max(self.limites_por_sexo.values()) if self.limites_por_sexo else None


NORMAS_SBC_2022: Dict[str, ReferenciaSBC2022] = {
    "FC": ReferenciaSBC2022(minimo=60, maximo=100, unidade="bpm"),
    "PR": ReferenciaSBC2022(minimo=120, maximo=200, unidade="ms"),
    "QRS": ReferenciaSBC2022(minimo=80, maximo=120, unidade="ms"),
    "QTc": ReferenciaSBC2022(
        minimo=None,
        maximo=None,
        unidade="ms",
        limites_por_sexo={"masculino": 450, "feminino": 460},
    ),
}


def avaliar_parametro(parametro: str, valor: Optional[float], sexo: Optional[str] = None) -> Dict[str, str]:
    """Avalia um parâmetro conforme faixas da SBC 2022.

    Retorna um dicionário com ``status`` (``normal``, ``limite``, ``alterado`` ou
    ``indisponivel``) e uma mensagem de referência.
    """

    parametro = parametro.upper()
    referencia = NORMAS_SBC_2022.get(parametro)
    if referencia is None:
        raise ValueError(f"Parâmetro não reconhecido: {parametro}")

    mensagem_base = f"Referência SBC 2022 para {parametro}: "
    if referencia.limites_por_sexo:
        limites = ", ".join(
            f"{sexo.upper()} ≤ {limite}{referencia.unidade}" for sexo, limite in referencia.limites_por_sexo.items()
        )
        mensagem_base += limites
    else:
        mensagem_base += f"{referencia.minimo}–{referencia.maximo}{referencia.unidade}"

    if valor is None:
        return {"status": "indisponivel", "mensagem": mensagem_base}

    # QTc utiliza limite superior dependente de sexo
    if referencia.limites_por_sexo:
        limite = referencia.limite_superior(sexo)
        if limite is None:
            return {"status": "indisponivel", "mensagem": mensagem_base}

        margem = 10
        status = "normal" if valor <= limite else "alterado"
        if limite - margem <= valor <= limite:
            status = "limite"
        return {"status": status, "mensagem": mensagem_base}

    assert referencia.minimo is not None and referencia.maximo is not None
    margem = 5
    if referencia.minimo <= valor <= referencia.maximo:
        status = "normal"
        if (valor - referencia.minimo) <= margem or (referencia.maximo - valor) <= margem:
            status = "limite"
    else:
        status = "alterado"
    return {"status": status, "mensagem": mensagem_base}
