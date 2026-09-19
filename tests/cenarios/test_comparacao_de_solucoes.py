from tests.cenarios.fabricas import aula_valida, cenario_de_ausencia, grade_minima

from gradeia.modules.cenarios import CENARIO_VIAVEL, AtribuicaoDeAula, SolucaoDeCenario
from gradeia.modules.cenarios.comparador import ComparadorDeSolucoes
from gradeia.modules.scheduling import OrToolsSchedulingEngine


def chave_lexicografica(solucao: SolucaoDeCenario) -> tuple[int, int, int, int]:
    return (
        solucao.quantidade_de_alteracoes,
        len(solucao.professores_afetados),
        solucao.quantidade_de_aulas_deslocadas,
        solucao.janelas_criadas,
    )


def grade_e_cenario_com_muitas_alternativas():
    professores = frozenset(
        {
            "PROFESSOR_001",
            "PROFESSOR_002",
            "PROFESSOR_003",
            "PROFESSOR_004",
        }
    )
    grade_base = grade_minima(
        professores=professores,
        aulas=(
            aula_valida(
                id_professor="PROFESSOR_001",
                id_disciplina="DISCIPLINA_001",
                id_turma="TURMA_001",
                dia=1,
                periodo=1,
            ),
        ),
    )
    janela = frozenset(
        (dia, periodo) for dia in (1, 2, 3) for periodo in (1, 2, 3, 4, 5, 6)
    )
    cenario = cenario_de_ausencia(
        id_professor="PROFESSOR_001",
        ausencia=frozenset({(1, 1)}),
        janela=janela,
    )
    return grade_base, cenario


def grade_e_cenario_de_impacto_unico():
    grade_base = grade_minima(
        aulas=(
            aula_valida(
                id_professor="PROFESSOR_001",
                id_disciplina="DISCIPLINA_001",
                id_turma="TURMA_001",
                dia=1,
                periodo=1,
            ),
            aula_valida(
                id_professor="PROFESSOR_002",
                id_disciplina="DISCIPLINA_002",
                id_turma="TURMA_002",
                dia=1,
                periodo=3,
            ),
        ),
    )
    cenario = cenario_de_ausencia(
        id_professor="PROFESSOR_001",
        ausencia=frozenset({(1, 1)}),
        janela=frozenset({(1, 1)}),
    )
    return grade_base, cenario


def grade_e_cenario_com_tuplas_distintas():
    professores = frozenset(
        {"PROFESSOR_001", "PROFESSOR_002", "PROFESSOR_003"}
    )
    grade_base = grade_minima(
        professores=professores,
        aulas=(
            aula_valida(
                id_professor="PROFESSOR_001",
                id_disciplina="DISCIPLINA_001",
                id_turma="TURMA_001",
                dia=1,
                periodo=1,
            ),
            aula_valida(
                id_professor="PROFESSOR_002",
                id_disciplina="DISCIPLINA_002",
                id_turma="TURMA_002",
                dia=1,
                periodo=3,
            ),
        ),
    )
    cenario = cenario_de_ausencia(
        id_professor="PROFESSOR_001",
        ausencia=frozenset({(1, 1)}),
        janela=frozenset({(1, 1), (1, 2)}),
    )
    return grade_base, cenario


def test_resultado_limita_a_cinco_solucoes_distintas():
    grade_base, cenario = grade_e_cenario_com_muitas_alternativas()

    resultado = OrToolsSchedulingEngine().simular(grade_base, cenario)

    assert resultado.status == CENARIO_VIAVEL
    assert 1 <= len(resultado.solucoes) <= 5
    assert len(resultado.solucoes) == 5
    estruturas = [solucao.atribuicoes for solucao in resultado.solucoes]
    assert len(set(estruturas)) == len(estruturas)


def test_solucao_expoe_todas_as_metricas_de_impacto():
    grade_base, cenario = grade_e_cenario_de_impacto_unico()

    resultado = OrToolsSchedulingEngine().simular(grade_base, cenario)

    assert resultado.status == CENARIO_VIAVEL
    assert len(resultado.solucoes) == 1
    solucao = resultado.solucoes[0]
    assert solucao.atribuicoes == (
        AtribuicaoDeAula(
            id_professor="PROFESSOR_002",
            id_disciplina="DISCIPLINA_001",
            id_turma="TURMA_001",
            dia=1,
            periodo=1,
        ),
        AtribuicaoDeAula(
            id_professor="PROFESSOR_002",
            id_disciplina="DISCIPLINA_002",
            id_turma="TURMA_002",
            dia=1,
            periodo=3,
        ),
    )
    # Aula 0: (P1, 1, 1) → (P2, 1, 1) = 1 alteração, 0 deslocada, {P1, P2}.
    # Aula 1 permanece. P2 no dia 1 passa de {3} para {1, 3} → 1 janela criada.
    assert solucao.quantidade_de_alteracoes == 1
    assert solucao.professores_afetados == frozenset(
        {"PROFESSOR_001", "PROFESSOR_002"}
    )
    assert solucao.quantidade_de_aulas_deslocadas == 0
    assert solucao.janelas_criadas == 1


def test_solucoes_sao_ordenadas_por_tupla_lexicografica_de_impacto():
    aulas_base = (
        aula_valida(
            id_professor="PROFESSOR_001",
            id_disciplina="DISCIPLINA_001",
            id_turma="TURMA_001",
            dia=1,
            periodo=1,
        ),
        aula_valida(
            id_professor="PROFESSOR_001",
            id_disciplina="DISCIPLINA_001",
            id_turma="TURMA_001",
            dia=1,
            periodo=2,
        ),
        aula_valida(
            id_professor="PROFESSOR_002",
            id_disciplina="DISCIPLINA_002",
            id_turma="TURMA_002",
            dia=1,
            periodo=3,
        ),
    )
    grade_base = grade_minima(
        professores=frozenset(
            {"PROFESSOR_001", "PROFESSOR_002", "PROFESSOR_003"}
        ),
        aulas=aulas_base,
    )
    poucas_alteracoes = SolucaoDeCenario(
        atribuicoes=(
            AtribuicaoDeAula(
                id_professor="PROFESSOR_003",
                id_disciplina="DISCIPLINA_001",
                id_turma="TURMA_001",
                dia=1,
                periodo=1,
            ),
            aulas_base[1],
            aulas_base[2],
        )
    )
    mesma_alt_com_janela = SolucaoDeCenario(
        atribuicoes=(
            AtribuicaoDeAula(
                id_professor="PROFESSOR_002",
                id_disciplina="DISCIPLINA_001",
                id_turma="TURMA_001",
                dia=1,
                periodo=1,
            ),
            aulas_base[1],
            aulas_base[2],
        )
    )
    mesma_alt_com_deslocamento = SolucaoDeCenario(
        atribuicoes=(
            AtribuicaoDeAula(
                id_professor="PROFESSOR_003",
                id_disciplina="DISCIPLINA_001",
                id_turma="TURMA_001",
                dia=1,
                periodo=4,
            ),
            aulas_base[1],
            aulas_base[2],
        )
    )
    muitas_alteracoes_um_professor = SolucaoDeCenario(
        atribuicoes=(
            AtribuicaoDeAula(
                id_professor="PROFESSOR_001",
                id_disciplina="DISCIPLINA_001",
                id_turma="TURMA_001",
                dia=2,
                periodo=1,
            ),
            AtribuicaoDeAula(
                id_professor="PROFESSOR_001",
                id_disciplina="DISCIPLINA_001",
                id_turma="TURMA_001",
                dia=2,
                periodo=2,
            ),
            aulas_base[2],
        )
    )

    # (1, 2, 0, 0), (1, 2, 0, 1), (1, 2, 1, 0), (2, 1, 2, 0)
    # Invertidas de propósito: se alterações não vierem antes de professores,
    # ou deslocadas antes de janelas, a ordem muda.
    ordenadas = ComparadorDeSolucoes().comparar(
        grade_base,
        (
            muitas_alteracoes_um_professor,
            mesma_alt_com_deslocamento,
            mesma_alt_com_janela,
            poucas_alteracoes,
        ),
    )

    assert [solucao.atribuicoes for solucao in ordenadas] == [
        poucas_alteracoes.atribuicoes,
        mesma_alt_com_janela.atribuicoes,
        mesma_alt_com_deslocamento.atribuicoes,
        muitas_alteracoes_um_professor.atribuicoes,
    ]
    assert [chave_lexicografica(solucao) for solucao in ordenadas] == [
        (1, 2, 0, 0),
        (1, 2, 0, 1),
        (1, 2, 1, 0),
        (2, 1, 2, 0),
    ]

    grade_simulada, cenario = grade_e_cenario_com_tuplas_distintas()
    resultado = OrToolsSchedulingEngine().simular(grade_simulada, cenario)
    assert resultado.status == CENARIO_VIAVEL
    assert len(resultado.solucoes) >= 2
    chaves = [chave_lexicografica(solucao) for solucao in resultado.solucoes]
    assert len(set(chaves)) >= 2
    assert resultado.solucoes == tuple(
        sorted(resultado.solucoes, key=chave_lexicografica)
    )


def test_mesma_entrada_produz_mesmas_solucoes_na_mesma_ordem():
    grade_base, cenario = grade_e_cenario_com_tuplas_distintas()
    motor = OrToolsSchedulingEngine()

    resultado1 = motor.simular(grade_base, cenario)
    resultado2 = motor.simular(grade_base, cenario)

    assert resultado1.status == CENARIO_VIAVEL
    assert resultado2.status == CENARIO_VIAVEL
    assert resultado1.solucoes == resultado2.solucoes
