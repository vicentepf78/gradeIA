from pathlib import Path

from gradeia.modules.cenarios import CENARIO_VIAVEL
from gradeia.modules.cenarios.carregar_dataset import carregar_simulacao
from gradeia.modules.scheduling import OrToolsSchedulingEngine

DATASET = Path(__file__).resolve().parents[2] / "dados" / "grade-basica.json"


def test_dataset_basico_produz_alternativas_viaveis():
    grade_base, cenario = carregar_simulacao(DATASET)

    assert len(grade_base.aulas) == 27
    assert cenario.ausencia.id_professor == "PROFESSOR_ANA"
    assert cenario.ausencia.turno == "MANHA"
    assert grade_base.perfil_da_turma("TURMA_8A").etapa == "FUNDAMENTAL"
    assert grade_base.perfil_da_turma("TURMA_9A").turno == "TARDE"

    resultado = OrToolsSchedulingEngine().simular(grade_base, cenario)

    assert resultado.status == CENARIO_VIAVEL
    assert 1 <= len(resultado.solucoes) <= 5
    dias = cenario.ausencia.dias or grade_base.dias
    for solucao in resultado.solucoes:
        for aula in solucao.atribuicoes:
            turno = grade_base.perfil_da_turma(aula.id_turma).turno
            if turno == "MANHA" and aula.dia in dias:
                assert aula.id_professor != "PROFESSOR_ANA"
