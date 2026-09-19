"""Fixtures determinísticas mínimas para as provas de S1."""

from gradeia.modules.cenarios import (
    JANELA_DE_ALTERACAO,
    AtribuicaoDeAula,
    AusenciaDeProfessor,
    Cenario,
    GradeBase,
    Professor,
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


def detalhes_dos_professores(
    professores: frozenset[str],
    disciplinas: frozenset[str] | None = None,
    dias: frozenset[int] | None = None,
    periodos: frozenset[int] | None = None,
    sobrescritas: dict[str, Professor] | None = None,
) -> tuple[Professor, ...]:
    disciplinas_padrao = disciplinas or frozenset({"DISCIPLINA_001", "DISCIPLINA_002"})
    dias_padrao = dias or frozenset({1, 2, 3, 4, 5})
    periodos_padrao = periodos or frozenset({1, 2, 3, 4, 5, 6})
    disponibilidade = frozenset(
        (dia, periodo) for dia in dias_padrao for periodo in periodos_padrao
    )
    por_id = {
        id_professor: Professor(
            id_professor=id_professor,
            disciplinas_habilitadas=disciplinas_padrao,
            disponibilidade=disponibilidade,
        )
        for id_professor in professores
    }
    if sobrescritas:
        por_id.update(sobrescritas)
    return tuple(por_id[id_professor] for id_professor in sorted(por_id))


def grade_minima(
    aulas: tuple[AtribuicaoDeAula, ...] | None = None,
    professores: frozenset[str] | None = None,
    detalhes: tuple[Professor, ...] | None = None,
) -> GradeBase:
    professores_da_grade = professores or frozenset({"PROFESSOR_001", "PROFESSOR_002"})
    disciplinas = frozenset({"DISCIPLINA_001", "DISCIPLINA_002"})
    dias = frozenset({1, 2, 3, 4, 5})
    periodos = frozenset({1, 2, 3, 4, 5, 6})
    return GradeBase(
        professores=professores_da_grade,
        disciplinas=disciplinas,
        turmas=frozenset({"TURMA_001", "TURMA_002"}),
        dias=dias,
        periodos=periodos,
        aulas=aulas if aulas is not None else (aula_valida(),),
        detalhes_dos_professores=(
            detalhes
            if detalhes is not None
            else detalhes_dos_professores(
                professores_da_grade,
                disciplinas=disciplinas,
                dias=dias,
                periodos=periodos,
            )
        ),
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
