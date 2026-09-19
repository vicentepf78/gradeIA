from tests.cenarios.espiao_solver import instalar_espiao_cp_model
from tests.cenarios.fabricas import aula_valida, cenario_de_ausencia, grade_minima

from gradeia.modules.cenarios import ERRO_VALIDACAO
from gradeia.modules.scheduling import OrToolsSchedulingEngine


def test_atribuicao_com_referencias_existentes_e_aceita():
    aula = aula_valida()
    grade_base = grade_minima(aulas=(aula,))

    assert aula.id_professor in grade_base.professores
    assert aula.id_disciplina in grade_base.disciplinas
    assert aula.id_turma in grade_base.turmas
    assert aula.dia in grade_base.dias
    assert aula.periodo in grade_base.periodos
    assert isinstance(aula.id_professor, str)
    assert isinstance(aula.id_disciplina, str)
    assert isinstance(aula.id_turma, str)
    assert isinstance(aula.dia, int)
    assert isinstance(aula.periodo, int)

    aulas_antes = grade_base.aulas
    resultado = OrToolsSchedulingEngine().simular(
        grade_base,
        cenario_de_ausencia(),
    )

    assert resultado.status != ERRO_VALIDACAO
    assert grade_base.aulas == aulas_antes


def test_referencias_inexistentes_sao_rejeitadas_antes_do_solver(monkeypatch):
    construcoes = instalar_espiao_cp_model(monkeypatch)
    motor = OrToolsSchedulingEngine()
    referencias_invalidas = (
        ("id_professor", "PROFESSOR_INEXISTENTE"),
        ("id_turma", "TURMA_INEXISTENTE"),
        ("id_disciplina", "DISCIPLINA_INEXISTENTE"),
        ("dia", 9),
        ("periodo", 9),
    )

    for campo, valor_invalido in referencias_invalidas:
        grade_base = grade_minima(aulas=(aula_valida(**{campo: valor_invalido}),))
        resultado = motor.simular(grade_base, cenario_de_ausencia())

        assert resultado.status == ERRO_VALIDACAO, campo
        assert construcoes == [], campo
