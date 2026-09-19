from tests.cenarios.espiao_solver import instalar_espiao_cp_model
from tests.cenarios.fabricas import (
    aula_valida,
    cenario_de_ausencia,
    detalhes_das_turmas,
    grade_minima,
)

from gradeia.modules.cenarios import (
    CENARIO_VIAVEL,
    ERRO_VALIDACAO,
    MANHA,
    MEDIO,
    NOITE,
    TARDE,
    Turma,
)
from gradeia.modules.scheduling import OrToolsSchedulingEngine


def test_ausencia_impede_alocacao_do_professor_no_turno():
    professor_ausente = "PROFESSOR_001"
    grade_base = grade_minima(
        aulas=(
            aula_valida(id_professor=professor_ausente, dia=1, periodo=1),
            aula_valida(
                id_professor=professor_ausente,
                id_disciplina="DISCIPLINA_002",
                id_turma="TURMA_002",
                dia=2,
                periodo=2,
            ),
        ),
    )
    cenario = cenario_de_ausencia(id_professor=professor_ausente, turno=MANHA)

    resultado = OrToolsSchedulingEngine().simular(grade_base, cenario)

    assert resultado.status == CENARIO_VIAVEL
    assert resultado.solucoes
    dias = grade_base.dias
    for solucao in resultado.solucoes:
        for atribuicao in solucao.atribuicoes:
            turno = grade_base.perfil_da_turma(atribuicao.id_turma).turno
            if turno == MANHA and atribuicao.dia in dias:
                assert atribuicao.id_professor != professor_ausente


def test_aulas_de_outros_turnos_sao_preservadas():
    aula_manha = aula_valida(dia=1, periodo=1)
    aula_tarde = aula_valida(
        id_turma="TURMA_TARDE",
        id_disciplina="DISCIPLINA_002",
        dia=1,
        periodo=1,
        turno=TARDE,
    )
    turmas = frozenset({"TURMA_001", "TURMA_TARDE"})
    grade_base = grade_minima(
        turmas=turmas,
        aulas=(aula_manha, aula_tarde),
        detalhes_turmas=detalhes_das_turmas(
            turmas,
            sobrescritas={
                "TURMA_001": Turma("TURMA_001", MANHA, MEDIO),
                "TURMA_TARDE": Turma("TURMA_TARDE", TARDE, MEDIO),
            },
        ),
    )

    resultado = OrToolsSchedulingEngine().simular(
        grade_base,
        cenario_de_ausencia(turno=MANHA, dias=frozenset({1})),
    )

    assert resultado.status == CENARIO_VIAVEL
    assert resultado.solucoes
    for solucao in resultado.solucoes:
        assert aula_tarde in solucao.atribuicoes
        preservada = next(
            aula for aula in solucao.atribuicoes if aula.id_turma == "TURMA_TARDE"
        )
        assert preservada.id_professor == aula_tarde.id_professor
        assert preservada.id_disciplina == aula_tarde.id_disciplina
        assert preservada.id_turma == aula_tarde.id_turma
        assert preservada.dia == aula_tarde.dia
        assert preservada.periodo == aula_tarde.periodo


def test_professor_ou_turno_inexistente_e_rejeitado_antes_do_solver(monkeypatch):
    construcoes = instalar_espiao_cp_model(monkeypatch)
    motor = OrToolsSchedulingEngine()
    grade_base = grade_minima()

    invalido_professor = cenario_de_ausencia(id_professor="PROFESSOR_INEXISTENTE")
    invalido_turno = cenario_de_ausencia(turno=NOITE)

    for cenario in (invalido_professor, invalido_turno):
        resultado = motor.simular(grade_base, cenario)
        assert resultado.status == ERRO_VALIDACAO
        assert construcoes == []


def test_ausencia_sem_aula_no_turno_devolve_grade_inalterada():
    aula_tarde = aula_valida(
        id_turma="TURMA_TARDE",
        dia=1,
        periodo=1,
        turno=TARDE,
    )
    turmas = frozenset({"TURMA_001", "TURMA_TARDE"})
    grade_base = grade_minima(
        turmas=turmas,
        aulas=(aula_tarde,),
        detalhes_turmas=detalhes_das_turmas(
            turmas,
            sobrescritas={
                "TURMA_001": Turma("TURMA_001", MANHA, MEDIO),
                "TURMA_TARDE": Turma("TURMA_TARDE", TARDE, MEDIO),
            },
        ),
    )

    resultado = OrToolsSchedulingEngine().simular(
        grade_base,
        cenario_de_ausencia(turno=MANHA),
    )

    assert resultado.status == CENARIO_VIAVEL
    assert len(resultado.solucoes) == 1
    solucao = resultado.solucoes[0]
    assert solucao.atribuicoes == grade_base.aulas
    assert solucao.quantidade_de_alteracoes == 0
