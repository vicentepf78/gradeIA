from tests.cenarios.fabricas import aula_valida, cenario_de_ausencia, grade_minima

from gradeia.modules.cenarios import CENARIO_VIAVEL
from gradeia.modules.scheduling import OrToolsSchedulingEngine


def test_ausencia_impede_alocacao_do_professor_na_janela():
    professor_ausente = "PROFESSOR_001"
    janela_da_manha = frozenset({(1, 1), (1, 2)})
    aula_na_manha = aula_valida(
        id_professor=professor_ausente,
        id_disciplina="DISCIPLINA_001",
        id_turma="TURMA_001",
        dia=1,
        periodo=1,
    )
    grade_base = grade_minima(aulas=(aula_na_manha,))
    cenario = cenario_de_ausencia(
        id_professor=professor_ausente,
        ausencia=janela_da_manha,
        janela=janela_da_manha,
    )

    resultado = OrToolsSchedulingEngine().simular(grade_base, cenario)

    assert resultado.status == CENARIO_VIAVEL
    assert resultado.solucoes
    for solucao in resultado.solucoes:
        for atribuicao in solucao.atribuicoes:
            if (atribuicao.dia, atribuicao.periodo) in cenario.ausencia.dias_periodos:
                assert atribuicao.id_professor != professor_ausente
