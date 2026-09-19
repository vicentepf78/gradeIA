from tests.cenarios.fabricas import (
    aula_valida,
    cenario_de_ausencia,
    detalhes_dos_professores,
    grade_minima,
)

from gradeia.modules.cenarios import CENARIO_INVIAVEL, Professor
from gradeia.modules.scheduling import OrToolsSchedulingEngine


def test_solver_sem_alternativa_retorna_cenario_inviavel_sem_solucao_parcial():
    professores = frozenset({"PROFESSOR_001", "PROFESSOR_002"})
    grade_base = grade_minima(
        professores=professores,
        aulas=(aula_valida(),),
        detalhes=detalhes_dos_professores(
            professores,
            sobrescritas={
                "PROFESSOR_002": Professor(
                    id_professor="PROFESSOR_002",
                    disciplinas_habilitadas=frozenset({"DISCIPLINA_002"}),
                    disponibilidade=frozenset({(2, 1), (2, 2)}),
                ),
            },
        ),
    )
    cenario = cenario_de_ausencia(
        ausencia=frozenset({(1, 1)}),
        janela=frozenset({(1, 1)}),
    )

    resultado = OrToolsSchedulingEngine().simular(grade_base, cenario)

    assert resultado.status == CENARIO_INVIAVEL
    assert resultado.solucoes == ()
