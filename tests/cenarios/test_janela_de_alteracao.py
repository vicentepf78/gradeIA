from tests.cenarios.espiao_solver import instalar_espiao_cp_model
from tests.cenarios.fabricas import aula_valida, cenario_de_ausencia, grade_minima

from gradeia.modules.cenarios import CENARIO_INVIAVEL
from gradeia.modules.scheduling import OrToolsSchedulingEngine


def test_janela_insuficiente_retorna_cenario_inviavel_com_aulas_afetadas(monkeypatch):
    construcoes = instalar_espiao_cp_model(monkeypatch)
    aula_na_janela = aula_valida(dia=1, periodo=1)
    aula_fora_da_janela = aula_valida(
        id_disciplina="DISCIPLINA_002",
        dia=1,
        periodo=2,
    )
    aula_nao_afetada = aula_valida(
        id_turma="TURMA_002",
        dia=2,
        periodo=1,
    )
    grade_base = grade_minima(
        aulas=(aula_na_janela, aula_fora_da_janela, aula_nao_afetada),
    )
    cenario = cenario_de_ausencia(
        ausencia=frozenset({(1, 1), (1, 2)}),
        janela=frozenset({(1, 1)}),
    )

    resultado = OrToolsSchedulingEngine().simular(grade_base, cenario)

    assert resultado.status == CENARIO_INVIAVEL
    assert aula_fora_da_janela in resultado.aulas_fora_da_janela
    assert aula_na_janela not in resultado.aulas_fora_da_janela
    assert aula_nao_afetada not in resultado.aulas_fora_da_janela
    assert resultado.aulas_fora_da_janela == (aula_fora_da_janela,)
    assert resultado.solucoes == ()
    assert construcoes == []
