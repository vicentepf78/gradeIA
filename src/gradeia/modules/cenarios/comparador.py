from collections import defaultdict

from gradeia.modules.cenarios.modelo import (
    AtribuicaoDeAula,
    GradeBase,
    SolucaoDeCenario,
)

LIMITE_DE_SOLUCOES = 5


class ComparadorDeSolucoes:
    def comparar(
        self,
        grade_base: GradeBase,
        solucoes: tuple[SolucaoDeCenario, ...] | list[SolucaoDeCenario],
    ) -> tuple[SolucaoDeCenario, ...]:
        enriquecidas: list[SolucaoDeCenario] = []
        vistas: set[tuple[AtribuicaoDeAula, ...]] = set()
        for solucao in solucoes:
            if solucao.atribuicoes in vistas:
                continue
            vistas.add(solucao.atribuicoes)
            enriquecidas.append(self._enriquecer(grade_base, solucao.atribuicoes))

        enriquecidas.sort(key=self._chave_de_ordenacao)
        return tuple(enriquecidas[:LIMITE_DE_SOLUCOES])

    def _enriquecer(
        self,
        grade_base: GradeBase,
        atribuicoes: tuple[AtribuicaoDeAula, ...],
    ) -> SolucaoDeCenario:
        quantidade_de_alteracoes = 0
        professores_afetados: set[str] = set()
        quantidade_de_aulas_deslocadas = 0
        for aula_base, aula_proposta in zip(
            grade_base.aulas, atribuicoes, strict=True
        ):
            if (
                aula_proposta.id_professor,
                aula_proposta.dia,
                aula_proposta.periodo,
            ) != (aula_base.id_professor, aula_base.dia, aula_base.periodo):
                quantidade_de_alteracoes += 1
                professores_afetados.add(aula_base.id_professor)
                professores_afetados.add(aula_proposta.id_professor)
            if (aula_proposta.dia, aula_proposta.periodo) != (
                aula_base.dia,
                aula_base.periodo,
            ):
                quantidade_de_aulas_deslocadas += 1

        return SolucaoDeCenario(
            atribuicoes=atribuicoes,
            quantidade_de_alteracoes=quantidade_de_alteracoes,
            professores_afetados=frozenset(professores_afetados),
            quantidade_de_aulas_deslocadas=quantidade_de_aulas_deslocadas,
            janelas_criadas=_janelas_criadas(grade_base.aulas, atribuicoes),
        )

    def _chave_de_ordenacao(
        self, solucao: SolucaoDeCenario
    ) -> tuple[int, int, int, int, tuple[tuple[str, str, str, int, int], ...]]:
        return (
            solucao.quantidade_de_alteracoes,
            len(solucao.professores_afetados),
            solucao.quantidade_de_aulas_deslocadas,
            solucao.janelas_criadas,
            _desempate_canonico(solucao.atribuicoes),
        )


def _janelas_de(atribuicoes: tuple[AtribuicaoDeAula, ...]) -> dict[tuple[str, int], int]:
    periodos_por_par: dict[tuple[str, int], set[int]] = defaultdict(set)
    for aula in atribuicoes:
        periodos_por_par[(aula.id_professor, aula.dia)].add(aula.periodo)

    janelas: dict[tuple[str, int], int] = {}
    for par, periodos in periodos_por_par.items():
        if len(periodos) < 2:
            janelas[par] = 0
            continue
        janelas[par] = max(0, max(periodos) - min(periodos) + 1 - len(periodos))
    return janelas


def _janelas_criadas(
    aulas_base: tuple[AtribuicaoDeAula, ...],
    atribuicoes: tuple[AtribuicaoDeAula, ...],
) -> int:
    janelas_base = _janelas_de(aulas_base)
    janelas_proposta = _janelas_de(atribuicoes)
    pares = set(janelas_base) | set(janelas_proposta)
    return sum(
        max(0, janelas_proposta.get(par, 0) - janelas_base.get(par, 0))
        for par in pares
    )


def _desempate_canonico(
    atribuicoes: tuple[AtribuicaoDeAula, ...],
) -> tuple[tuple[str, str, str, int, int], ...]:
    return tuple(
        (
            aula.id_professor,
            aula.id_disciplina,
            aula.id_turma,
            aula.dia,
            aula.periodo,
        )
        for aula in atribuicoes
    )
