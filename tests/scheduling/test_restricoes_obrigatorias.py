from collections import Counter

from tests.cenarios.fabricas import (
    aula_valida,
    cenario_de_ausencia,
    detalhes_dos_professores,
    grade_minima,
)

from gradeia.modules.cenarios import CENARIO_VIAVEL, Professor
from gradeia.modules.scheduling import OrToolsSchedulingEngine


def test_solucao_nao_cria_conflito_de_professor_nem_de_turma():
    aula_do_ausente = aula_valida(
        id_professor="PROFESSOR_001",
        id_disciplina="DISCIPLINA_001",
        id_turma="TURMA_001",
        dia=1,
        periodo=1,
    )
    aula_da_mesma_turma = aula_valida(
        id_professor="PROFESSOR_002",
        id_disciplina="DISCIPLINA_002",
        id_turma="TURMA_001",
        dia=1,
        periodo=2,
    )
    grade_base = grade_minima(aulas=(aula_do_ausente, aula_da_mesma_turma))
    cenario = cenario_de_ausencia(
        ausencia=frozenset({(1, 1)}),
        janela=frozenset({(1, 1), (1, 2)}),
    )

    resultado = OrToolsSchedulingEngine().simular(grade_base, cenario)

    assert resultado.status == CENARIO_VIAVEL
    assert resultado.solucoes
    for solucao in resultado.solucoes:
        ocupacao_professor: set[tuple[str, int, int]] = set()
        ocupacao_turma: set[tuple[str, int, int]] = set()
        for atribuicao in solucao.atribuicoes:
            chave_professor = (
                atribuicao.id_professor,
                atribuicao.dia,
                atribuicao.periodo,
            )
            chave_turma = (atribuicao.id_turma, atribuicao.dia, atribuicao.periodo)
            assert chave_professor not in ocupacao_professor
            assert chave_turma not in ocupacao_turma
            ocupacao_professor.add(chave_professor)
            ocupacao_turma.add(chave_turma)


def test_solucao_respeita_habilitacao_e_disponibilidade_do_professor():
    professores = frozenset(
        {"PROFESSOR_001", "PROFESSOR_002", "PROFESSOR_003", "PROFESSOR_004"}
    )
    grade_base = grade_minima(
        professores=professores,
        aulas=(aula_valida(),),
        detalhes=detalhes_dos_professores(
            professores,
            sobrescritas={
                "PROFESSOR_003": Professor(
                    id_professor="PROFESSOR_003",
                    disciplinas_habilitadas=frozenset({"DISCIPLINA_002"}),
                    disponibilidade=frozenset(
                        (dia, periodo)
                        for dia in (1, 2, 3, 4, 5)
                        for periodo in (1, 2, 3, 4, 5, 6)
                    ),
                ),
                "PROFESSOR_004": Professor(
                    id_professor="PROFESSOR_004",
                    disciplinas_habilitadas=frozenset(
                        {"DISCIPLINA_001", "DISCIPLINA_002"}
                    ),
                    disponibilidade=frozenset({(2, 1), (2, 2)}),
                ),
            },
        ),
    )
    perfis = {
        perfil.id_professor: perfil for perfil in grade_base.detalhes_dos_professores
    }
    cenario = cenario_de_ausencia(
        ausencia=frozenset({(1, 1)}),
        janela=frozenset({(1, 1)}),
    )

    resultado = OrToolsSchedulingEngine().simular(grade_base, cenario)

    assert resultado.status == CENARIO_VIAVEL
    assert resultado.solucoes
    for solucao in resultado.solucoes:
        for atribuicao in solucao.atribuicoes:
            perfil = perfis[atribuicao.id_professor]
            assert atribuicao.id_disciplina in perfil.disciplinas_habilitadas
            assert (atribuicao.dia, atribuicao.periodo) in perfil.disponibilidade


def test_solucao_preserva_quantidade_de_aulas_por_turma_e_disciplina():
    aulas = (
        aula_valida(
            id_professor="PROFESSOR_001",
            id_disciplina="DISCIPLINA_001",
            id_turma="TURMA_001",
            dia=1,
            periodo=1,
        ),
        aula_valida(
            id_professor="PROFESSOR_002",
            id_disciplina="DISCIPLINA_001",
            id_turma="TURMA_001",
            dia=1,
            periodo=2,
        ),
        aula_valida(
            id_professor="PROFESSOR_001",
            id_disciplina="DISCIPLINA_002",
            id_turma="TURMA_001",
            dia=2,
            periodo=1,
        ),
        aula_valida(
            id_professor="PROFESSOR_002",
            id_disciplina="DISCIPLINA_001",
            id_turma="TURMA_002",
            dia=2,
            periodo=2,
        ),
    )
    grade_base = grade_minima(aulas=aulas)
    carga_da_base = Counter(
        (aula.id_turma, aula.id_disciplina) for aula in grade_base.aulas
    )
    cenario = cenario_de_ausencia(
        ausencia=frozenset({(1, 1)}),
        janela=frozenset({(1, 1), (1, 2)}),
    )

    resultado = OrToolsSchedulingEngine().simular(grade_base, cenario)

    assert resultado.status == CENARIO_VIAVEL
    assert resultado.solucoes
    for solucao in resultado.solucoes:
        carga_da_solucao = Counter(
            (aula.id_turma, aula.id_disciplina) for aula in solucao.atribuicoes
        )
        assert carga_da_solucao == carga_da_base


def test_solucao_preserva_atribuicoes_fora_da_janela_de_alteracao():
    aula_dentro_da_janela = aula_valida(
        id_professor="PROFESSOR_001",
        id_disciplina="DISCIPLINA_001",
        id_turma="TURMA_001",
        dia=1,
        periodo=1,
    )
    aula_fora_da_janela = aula_valida(
        id_professor="PROFESSOR_002",
        id_disciplina="DISCIPLINA_002",
        id_turma="TURMA_002",
        dia=3,
        periodo=4,
    )
    grade_base = grade_minima(aulas=(aula_dentro_da_janela, aula_fora_da_janela))
    cenario = cenario_de_ausencia(
        ausencia=frozenset({(1, 1)}),
        janela=frozenset({(1, 1), (1, 2)}),
    )

    resultado = OrToolsSchedulingEngine().simular(grade_base, cenario)

    assert resultado.status == CENARIO_VIAVEL
    assert resultado.solucoes
    for solucao in resultado.solucoes:
        assert aula_fora_da_janela in solucao.atribuicoes
        preservada = next(
            atribuicao
            for atribuicao in solucao.atribuicoes
            if atribuicao == aula_fora_da_janela
        )
        assert preservada.id_professor == aula_fora_da_janela.id_professor
        assert preservada.id_disciplina == aula_fora_da_janela.id_disciplina
        assert preservada.id_turma == aula_fora_da_janela.id_turma
        assert preservada.dia == aula_fora_da_janela.dia
        assert preservada.periodo == aula_fora_da_janela.periodo
