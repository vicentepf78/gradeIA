from tests.cenarios.espiao_solver import instalar_espiao_cp_model
from tests.cenarios.fabricas import (
    aula_valida,
    cenario_de_ausencia,
    detalhes_das_turmas,
    grade_minima,
)

from gradeia.modules.cenarios import (
    ERRO_VALIDACAO,
    FUNDAMENTAL,
    MANHA,
    MEDIO,
    NOITE,
    TARDE,
    TURNOS_VALIDOS,
    Turma,
)
from gradeia.modules.scheduling import OrToolsSchedulingEngine


def test_turma_possui_exatamente_um_turno_valido():
    turmas = frozenset({"TURMA_MANHA", "TURMA_TARDE", "TURMA_NOITE"})
    grade_base = grade_minima(
        turmas=turmas,
        aulas=(
            aula_valida(id_turma="TURMA_MANHA"),
            aula_valida(id_turma="TURMA_TARDE", id_disciplina="DISCIPLINA_002"),
            aula_valida(id_turma="TURMA_NOITE", dia=2),
        ),
        detalhes_turmas=detalhes_das_turmas(
            turmas,
            sobrescritas={
                "TURMA_MANHA": Turma("TURMA_MANHA", MANHA, MEDIO),
                "TURMA_TARDE": Turma("TURMA_TARDE", TARDE, MEDIO),
                "TURMA_NOITE": Turma("TURMA_NOITE", NOITE, MEDIO),
            },
        ),
    )

    turnos = {grade_base.perfil_da_turma(id_turma).turno for id_turma in grade_base.turmas}
    assert turnos == TURNOS_VALIDOS
    for id_turma in grade_base.turmas:
        assert grade_base.perfil_da_turma(id_turma).turno in TURNOS_VALIDOS


def test_turma_possui_exatamente_uma_etapa_valida():
    turmas = frozenset({"TURMA_FUND", "TURMA_MEDIO"})
    grade_base = grade_minima(
        turmas=turmas,
        aulas=(
            aula_valida(id_turma="TURMA_FUND"),
            aula_valida(id_turma="TURMA_MEDIO", id_disciplina="DISCIPLINA_002"),
        ),
        detalhes_turmas=detalhes_das_turmas(
            turmas,
            sobrescritas={
                "TURMA_FUND": Turma("TURMA_FUND", MANHA, FUNDAMENTAL),
                "TURMA_MEDIO": Turma("TURMA_MEDIO", TARDE, MEDIO),
            },
        ),
    )

    assert grade_base.perfil_da_turma("TURMA_FUND").etapa == FUNDAMENTAL
    assert grade_base.perfil_da_turma("TURMA_MEDIO").etapa == MEDIO


def test_teto_de_periodos_segue_a_etapa_da_turma():
    turmas = frozenset({"TURMA_FUND", "TURMA_MEDIO"})
    grade_base = grade_minima(
        turmas=turmas,
        aulas=(
            aula_valida(id_turma="TURMA_FUND", periodo=5),
            aula_valida(
                id_turma="TURMA_MEDIO",
                id_disciplina="DISCIPLINA_002",
                id_professor="PROFESSOR_002",
                periodo=6,
            ),
        ),
        detalhes_turmas=detalhes_das_turmas(
            turmas,
            sobrescritas={
                "TURMA_FUND": Turma("TURMA_FUND", MANHA, FUNDAMENTAL),
                "TURMA_MEDIO": Turma("TURMA_MEDIO", TARDE, MEDIO),
            },
        ),
    )

    assert grade_base.perfil_da_turma("TURMA_FUND").teto_de_periodos == 5
    assert grade_base.perfil_da_turma("TURMA_MEDIO").teto_de_periodos == 6
    resultado = OrToolsSchedulingEngine().simular(
        grade_base,
        cenario_de_ausencia(id_professor="PROFESSOR_002", turno=TARDE),
    )
    assert resultado.status != ERRO_VALIDACAO


def test_periodo_ou_turno_incompativel_e_rejeitado_antes_do_solver(monkeypatch):
    construcoes = instalar_espiao_cp_model(monkeypatch)
    motor = OrToolsSchedulingEngine()
    turmas = frozenset({"TURMA_FUND"})
    detalhes = detalhes_das_turmas(
        turmas,
        sobrescritas={"TURMA_FUND": Turma("TURMA_FUND", MANHA, FUNDAMENTAL)},
    )

    grade_periodo_invalido = grade_minima(
        turmas=turmas,
        aulas=(aula_valida(id_turma="TURMA_FUND", periodo=6),),
        detalhes_turmas=detalhes,
    )
    grade_turno_incompativel = grade_minima(
        turmas=turmas,
        aulas=(aula_valida(id_turma="TURMA_FUND", turno=TARDE),),
        detalhes_turmas=detalhes,
    )

    for grade_base in (grade_periodo_invalido, grade_turno_incompativel):
        resultado = motor.simular(grade_base, cenario_de_ausencia())
        assert resultado.status == ERRO_VALIDACAO
        assert construcoes == []
