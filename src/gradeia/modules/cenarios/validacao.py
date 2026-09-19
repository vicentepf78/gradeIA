from gradeia.modules.cenarios.modelo import (
    JANELA_DE_ALTERACAO,
    AtribuicaoDeAula,
    Cenario,
    GradeBase,
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
        if aula.periodo not in grade_base.periodos:
            return False
    return True


def aulas_afetadas_pela_ausencia(
    grade_base: GradeBase,
    cenario: Cenario,
) -> tuple[AtribuicaoDeAula, ...]:
    ausencia = cenario.ausencia
    return tuple(
        aula
        for aula in grade_base.aulas
        if aula.id_professor == ausencia.id_professor
        and (aula.dia, aula.periodo) in ausencia.dias_periodos
    )


def janela_de_alteracao(cenario: Cenario) -> frozenset[tuple[int, int]]:
    for restricao in cenario.restricoes:
        if restricao.tipo == JANELA_DE_ALTERACAO:
            return restricao.dias_periodos
    return frozenset()


def aulas_fora_da_janela_de_alteracao(
    grade_base: GradeBase,
    cenario: Cenario,
) -> tuple[AtribuicaoDeAula, ...]:
    janela = janela_de_alteracao(cenario)
    return tuple(
        aula
        for aula in aulas_afetadas_pela_ausencia(grade_base, cenario)
        if (aula.dia, aula.periodo) not in janela
    )
