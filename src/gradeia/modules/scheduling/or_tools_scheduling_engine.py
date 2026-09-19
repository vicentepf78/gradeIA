from ortools.sat.python import cp_model

from gradeia.modules.cenarios import (
    CENARIO_INVIAVEL,
    CENARIO_VIAVEL,
    ERRO_VALIDACAO,
    AtribuicaoDeAula,
    Cenario,
    GradeBase,
    ResultadoDaSimulacao,
    SolucaoDeCenario,
)
from gradeia.modules.cenarios.validacao import (
    aulas_fora_da_janela_de_alteracao,
    janela_de_alteracao,
    referencias_da_grade_sao_validas,
)
from gradeia.modules.scheduling.porta import SchedulingEngine

TETO_INTERNO_DE_SOLUCOES = 20
LIMITE_DE_TEMPO_EM_SEGUNDOS = 10.0
SEMENTE_ALEATORIA = 1


class ColetorDeSolucoes(cp_model.CpSolverSolutionCallback):
    def __init__(self, montar_atribuicoes, teto: int) -> None:
        super().__init__()
        self._montar_atribuicoes = montar_atribuicoes
        self._teto = teto
        self.solucoes: list[SolucaoDeCenario] = []
        self._vistas: set[tuple[AtribuicaoDeAula, ...]] = set()

    def on_solution_callback(self) -> None:
        atribuicoes = self._montar_atribuicoes(self)
        if atribuicoes is None or atribuicoes in self._vistas:
            return
        self._vistas.add(atribuicoes)
        self.solucoes.append(SolucaoDeCenario(atribuicoes=atribuicoes))
        if len(self.solucoes) >= self._teto:
            self.stop_search()


class OrToolsSchedulingEngine(SchedulingEngine):
    def simular(self, grade_base: GradeBase, cenario: Cenario) -> ResultadoDaSimulacao:
        if not referencias_da_grade_sao_validas(grade_base):
            return ResultadoDaSimulacao(status=ERRO_VALIDACAO)

        aulas_fora = aulas_fora_da_janela_de_alteracao(grade_base, cenario)
        if aulas_fora:
            return ResultadoDaSimulacao(
                status=CENARIO_INVIAVEL,
                aulas_fora_da_janela=aulas_fora,
            )

        return self._resolver(grade_base, cenario)

    def _resolver(self, grade_base: GradeBase, cenario: Cenario) -> ResultadoDaSimulacao:
        janela = janela_de_alteracao(cenario)
        id_ausente = cenario.ausencia.id_professor
        slots_de_ausencia = cenario.ausencia.dias_periodos

        aulas_fixas: dict[int, AtribuicaoDeAula] = {}
        aulas_moveis: list[int] = []
        for indice, aula in enumerate(grade_base.aulas):
            if (aula.dia, aula.periodo) in janela:
                aulas_moveis.append(indice)
            else:
                aulas_fixas[indice] = aula

        if not aulas_moveis:
            return ResultadoDaSimulacao(
                status=CENARIO_VIAVEL,
                solucoes=(SolucaoDeCenario(atribuicoes=grade_base.aulas),),
            )

        ocupacao_professor = {
            (aula.id_professor, aula.dia, aula.periodo)
            for aula in aulas_fixas.values()
        }
        ocupacao_turma = {
            (aula.id_turma, aula.dia, aula.periodo) for aula in aulas_fixas.values()
        }

        candidatos_por_aula: dict[int, list[tuple[str, int, int]]] = {}
        for indice in aulas_moveis:
            aula = grade_base.aulas[indice]
            candidatos: list[tuple[str, int, int]] = []
            for id_professor in grade_base.professores:
                perfil = grade_base.perfil_do_professor(id_professor)
                if aula.id_disciplina not in perfil.disciplinas_habilitadas:
                    continue
                for dia, periodo in janela:
                    if (dia, periodo) not in perfil.disponibilidade:
                        continue
                    if id_professor == id_ausente and (dia, periodo) in slots_de_ausencia:
                        continue
                    if (id_professor, dia, periodo) in ocupacao_professor:
                        continue
                    if (aula.id_turma, dia, periodo) in ocupacao_turma:
                        continue
                    candidatos.append((id_professor, dia, periodo))
            if not candidatos:
                return ResultadoDaSimulacao(status=CENARIO_INVIAVEL)
            candidatos_por_aula[indice] = candidatos

        model = cp_model.CpModel()
        variaveis = {}
        for indice, candidatos in candidatos_por_aula.items():
            for id_professor, dia, periodo in candidatos:
                variaveis[(indice, id_professor, dia, periodo)] = model.new_bool_var(
                    f"aula_{indice}_{id_professor}_{dia}_{periodo}"
                )
            model.add(
                sum(
                    variaveis[(indice, id_professor, dia, periodo)]
                    for id_professor, dia, periodo in candidatos
                )
                == 1
            )

        for id_professor in grade_base.professores:
            for dia, periodo in janela:
                grupo = [
                    var
                    for (indice, professor, dia_var, periodo_var), var in variaveis.items()
                    if professor == id_professor
                    and dia_var == dia
                    and periodo_var == periodo
                ]
                if len(grupo) > 1:
                    model.add(sum(grupo) <= 1)

        for id_turma in grade_base.turmas:
            for dia, periodo in janela:
                grupo = [
                    var
                    for (indice, _professor, dia_var, periodo_var), var in variaveis.items()
                    if grade_base.aulas[indice].id_turma == id_turma
                    and dia_var == dia
                    and periodo_var == periodo
                ]
                if len(grupo) > 1:
                    model.add(sum(grupo) <= 1)

        def montar_atribuicoes(callback) -> tuple[AtribuicaoDeAula, ...] | None:
            atribuicoes: list[AtribuicaoDeAula] = []
            for indice, aula in enumerate(grade_base.aulas):
                if indice in aulas_fixas:
                    atribuicoes.append(aula)
                    continue
                escolhida = None
                for (i, id_professor, dia, periodo), var in variaveis.items():
                    if i != indice:
                        continue
                    if callback.boolean_value(var):
                        escolhida = AtribuicaoDeAula(
                            id_professor=id_professor,
                            id_disciplina=aula.id_disciplina,
                            id_turma=aula.id_turma,
                            dia=dia,
                            periodo=periodo,
                        )
                        break
                if escolhida is None:
                    return None
                atribuicoes.append(escolhida)
            return tuple(atribuicoes)

        coletor = ColetorDeSolucoes(montar_atribuicoes, TETO_INTERNO_DE_SOLUCOES)
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = LIMITE_DE_TEMPO_EM_SEGUNDOS
        solver.parameters.random_seed = SEMENTE_ALEATORIA
        solver.parameters.num_search_workers = 1
        solver.parameters.enumerate_all_solutions = True
        solver.solve(model, coletor)

        if not coletor.solucoes:
            return ResultadoDaSimulacao(status=CENARIO_INVIAVEL)
        return ResultadoDaSimulacao(
            status=CENARIO_VIAVEL,
            solucoes=tuple(coletor.solucoes),
        )
