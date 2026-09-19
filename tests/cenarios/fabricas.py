"""Fixtures determinísticas mínimas para as provas de S1."""

from gradeia.modules.cenarios import (
    JANELA_DE_ALTERACAO,
    AtribuicaoDeAula,
    AusenciaDeProfessor,
    Cenario,
    GradeBase,
    RestricaoDeCenario,
)


def aula_valida(**sobrescritas: object) -> AtribuicaoDeAula:
    dados = {
        "id_professor": "PROFESSOR_001",
        "id_disciplina": "DISCIPLINA_001",
        "id_turma": "TURMA_001",
        "dia": 1,
        "periodo": 1,
    }
    dados.update(sobrescritas)
    return AtribuicaoDeAula(**dados)


def grade_minima(aulas: tuple[AtribuicaoDeAula, ...] | None = None) -> GradeBase:
    return GradeBase(
        professores=frozenset({"PROFESSOR_001", "PROFESSOR_002"}),
        disciplinas=frozenset({"DISCIPLINA_001", "DISCIPLINA_002"}),
        turmas=frozenset({"TURMA_001", "TURMA_002"}),
        dias=frozenset({1, 2, 3, 4, 5}),
        periodos=frozenset({1, 2, 3, 4, 5, 6}),
        aulas=aulas if aulas is not None else (aula_valida(),),
    )


def cenario_de_ausencia(
    id_professor: str = "PROFESSOR_001",
    ausencia: frozenset[tuple[int, int]] | None = None,
    janela: frozenset[tuple[int, int]] | None = None,
) -> Cenario:
    dias_periodos_ausencia = ausencia if ausencia is not None else frozenset({(1, 1)})
    dias_periodos_janela = janela if janela is not None else dias_periodos_ausencia
    return Cenario(
        ausencia=AusenciaDeProfessor(
            id_professor=id_professor,
            dias_periodos=dias_periodos_ausencia,
        ),
        restricoes=(
            RestricaoDeCenario(
                tipo=JANELA_DE_ALTERACAO,
                dias_periodos=dias_periodos_janela,
            ),
        ),
    )
