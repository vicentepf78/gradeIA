from gradeia.modules.cenarios.modelo import (
    ETAPAS_VALIDAS,
    JANELA_DE_ALTERACAO,
    TURNOS_VALIDOS,
    AtribuicaoDeAula,
    Cenario,
    GradeBase,
    Turma,
)


def referencias_da_grade_sao_validas(grade_base: GradeBase) -> bool:
    for aula in grade_base.aulas:
        if aula.id_professor not in grade_base.professores:
            return False
        if aula.id_disciplina not in grade_base.disciplinas:
            return False
        if aula.id_turma not in grade_base.turmas:
            return False
        if aula.dia not in grade_base.dias:
            return False
        turma = grade_base.perfil_da_turma(aula.id_turma)
        if not _turma_eh_valida(turma):
            return False
        if aula.periodo < 1 or aula.periodo > turma.teto_de_periodos:
            return False
        if aula.turno is not None and aula.turno != turma.turno:
            return False
    return True


def ausencia_eh_valida(grade_base: GradeBase, cenario: Cenario) -> bool:
    if cenario.ausencia.id_professor not in grade_base.professores:
        return False
    if cenario.ausencia.turno not in TURNOS_VALIDOS:
        return False
    turnos_da_grade = {grade_base.perfil_da_turma(id_turma).turno for id_turma in grade_base.turmas}
    return cenario.ausencia.turno in turnos_da_grade


def dias_cobertos_pela_ausencia(grade_base: GradeBase, cenario: Cenario) -> frozenset[int]:
    if cenario.ausencia.dias:
        return cenario.ausencia.dias
    return grade_base.dias


def turno_da_aula(grade_base: GradeBase, aula: AtribuicaoDeAula) -> str:
    return grade_base.perfil_da_turma(aula.id_turma).turno


def aulas_afetadas_pela_ausencia(
    grade_base: GradeBase,
    cenario: Cenario,
) -> tuple[AtribuicaoDeAula, ...]:
    dias = dias_cobertos_pela_ausencia(grade_base, cenario)
    return tuple(
        aula
        for aula in grade_base.aulas
        if aula.id_professor == cenario.ausencia.id_professor
        and turno_da_aula(grade_base, aula) == cenario.ausencia.turno
        and aula.dia in dias
    )


def janela_de_alteracao(
    grade_base: GradeBase,
    cenario: Cenario,
) -> frozenset[tuple[int, int]]:
    for restricao in cenario.restricoes:
        if restricao.tipo == JANELA_DE_ALTERACAO:
            return restricao.dias_periodos
    dias = dias_cobertos_pela_ausencia(grade_base, cenario)
    periodos = _periodos_do_turno(grade_base, cenario.ausencia.turno)
    return frozenset((dia, periodo) for dia in dias for periodo in periodos)


def aulas_fora_da_janela_de_alteracao(
    grade_base: GradeBase,
    cenario: Cenario,
) -> tuple[AtribuicaoDeAula, ...]:
    janela = janela_de_alteracao(grade_base, cenario)
    return tuple(
        aula
        for aula in aulas_afetadas_pela_ausencia(grade_base, cenario)
        if (aula.dia, aula.periodo) not in janela
    )


def _turma_eh_valida(turma: Turma) -> bool:
    return turma.turno in TURNOS_VALIDOS and turma.etapa in ETAPAS_VALIDAS


def _periodos_do_turno(grade_base: GradeBase, turno: str) -> range:
    teto = 1
    for id_turma in grade_base.turmas:
        turma = grade_base.perfil_da_turma(id_turma)
        if turma.turno == turno:
            teto = max(teto, turma.teto_de_periodos)
    return range(1, teto + 1)
