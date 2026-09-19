from dataclasses import dataclass

from gradeia.modules.cenarios.modelo import AtribuicaoDeAula, SolucaoDeCenario

CENARIO_VIAVEL = "CENARIO_VIAVEL"
CENARIO_INVIAVEL = "CENARIO_INVIAVEL"
ERRO_VALIDACAO = "ERRO_VALIDACAO"


@dataclass(frozen=True)
class ResultadoDaSimulacao:
    status: str
    solucoes: tuple[SolucaoDeCenario, ...] = ()
    aulas_fora_da_janela: tuple[AtribuicaoDeAula, ...] = ()
