"""Espião de CpModel que não depende do OR-Tools estar instalado."""

from __future__ import annotations

import sys
import types


def instalar_espiao_cp_model(monkeypatch) -> list[bool]:
    construcoes: list[bool] = []

    class CpModelEspiao:
        def __init__(self, *args, **kwargs):
            construcoes.append(True)

    try:
        import ortools.sat.python.cp_model as cp_model

        monkeypatch.setattr(cp_model, "CpModel", CpModelEspiao)
    except ImportError:
        for nome in ("ortools", "ortools.sat", "ortools.sat.python"):
            if nome not in sys.modules:
                modulo = types.ModuleType(nome)
                modulo.__path__ = []
                monkeypatch.setitem(sys.modules, nome, modulo)
        falso = types.ModuleType("ortools.sat.python.cp_model")
        falso.CpModel = CpModelEspiao
        monkeypatch.setitem(sys.modules, "ortools.sat.python.cp_model", falso)
        monkeypatch.setattr(
            sys.modules["ortools.sat.python"],
            "cp_model",
            falso,
            raising=False,
        )

    return construcoes
