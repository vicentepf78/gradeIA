"""Fixtures determinísticas mínimas para as provas."""

from gradeia.modules.cenarios import (
    JANELA_DE_ALTERACAO,
    MANHA,
    MEDIO,
    AtribuicaoDeAula,
    AusenciaDeProfessor,
    Cenario,
    GradeBase,
    Professor,
    RestricaoDeCenario,
    Turma,
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


def detalhes_das_turmas(
    turmas: frozenset[str],
    turno: str = MANHA,
    etapa: str = MEDIO,
    sobrescritas: dict[str, Turma] | None = None,
) -> tuple[Turma, ...]:
    por_id = {
        id_turma: Turma(id_turma=id_turma, turno=turno, etapa=etapa)
        for id_turma in turmas
    }
    if sobrescritas:
        por_id.update(sobrescritas)
    return tuple(por_id[id_turma] for id_turma in sorted(por_id))


def grade_minima(
    aulas: tuple[AtribuicaoDeAula, ...] | None = None,
    professores: frozenset[str] | None = None,
    detalhes: tuple[Professor, ...] | None = None,
    turmas: frozenset[str] | None = None,
    detalhes_turmas: tuple[Turma, ...] | None = None,
) -> GradeBase:
    professores_da_grade = professores or frozenset({"PROFESSOR_001", "PROFESSOR_002"})
    turmas_da_grade = turmas or frozenset({"TURMA_001", "TURMA_002"})
    disciplinas = frozenset({"DISCIPLINA_001", "DISCIPLINA_002"})
    dias = frozenset({1, 2, 3, 4, 5})
    periodos = frozenset({1, 2, 3, 4, 5, 6})
    return GradeBase(
        professores=professores_da_grade,
        disciplinas=disciplinas,
        turmas=turmas_da_grade,
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
        detalhes_das_turmas=(
            detalhes_turmas
            if detalhes_turmas is not None
            else detalhes_das_turmas(turmas_da_grade)
        ),
    )


def cenario_de_ausencia(
    id_professor: str = "PROFESSOR_001",
    turno: str = MANHA,
    dias: frozenset[int] | None = None,
    janela: frozenset[tuple[int, int]] | None = None,
    ausencia: frozenset[tuple[int, int]] | None = None,
) -> Cenario:
    dias_da_falta = dias
    if ausencia is not None:
        dias_da_falta = frozenset(dia for dia, _periodo in ausencia)
        if janela is None:
            janela = ausencia
    restricoes = ()
    if janela is not None:
        restricoes = (
            RestricaoDeCenario(
                tipo=JANELA_DE_ALTERACAO,
                dias_periodos=janela,
            ),
        )
    return Cenario(
        ausencia=AusenciaDeProfessor(
            id_professor=id_professor,
            turno=turno,
            dias=dias_da_falta or frozenset(),
        ),
        restricoes=restricoes,
    )
