from gradeia.modules.cenarios import (
    CENARIO_INVIAVEL,
    CENARIO_VIAVEL,
    ERRO_VALIDACAO,
    Cenario,
    GradeBase,
    ResultadoDaSimulacao,
)
from gradeia.modules.cenarios.validacao import (
    aulas_fora_da_janela_de_alteracao,
    referencias_da_grade_sao_validas,
)
from gradeia.modules.scheduling.porta import SchedulingEngine


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

        return ResultadoDaSimulacao(status=CENARIO_VIAVEL)
