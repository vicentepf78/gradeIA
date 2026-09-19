import sys
from pathlib import Path

from gradeia.modules.cenarios.carregar_dataset import DATASET_PADRAO, carregar_simulacao
from gradeia.modules.cenarios.resultado import CENARIO_INVIAVEL, ERRO_VALIDACAO
from gradeia.modules.scheduling import OrToolsSchedulingEngine

NOMES_DOS_DIAS = {
    1: "segunda",
    2: "terca",
    3: "quarta",
    4: "quinta",
    5: "sexta",
}


def main(argv: list[str] | None = None) -> int:
    argumentos = sys.argv[1:] if argv is None else argv
    caminho = Path(argumentos[0]) if argumentos else DATASET_PADRAO
    if not caminho.is_file():
        print(f"Dataset não encontrado: {caminho}")
        print("Execute o comando na raiz do repositório gradeIA.")
        return 1

    grade_base, cenario = carregar_simulacao(caminho)
    resultado = OrToolsSchedulingEngine().simular(grade_base, cenario)

    print(f"Dataset: {caminho}")
    print(f"Aulas na grade base: {len(grade_base.aulas)}")
    print(f"Professor ausente: {cenario.ausencia.id_professor}")
    print(f"Turno da falta: {cenario.ausencia.turno}")
    print(f"Status: {resultado.status}")

    if resultado.status == ERRO_VALIDACAO:
        print("A grade contém referência inexistente. Corrija o dataset.")
        return 1
    if resultado.status == CENARIO_INVIAVEL:
        if resultado.aulas_fora_da_janela:
            print("Aulas afetadas fora da janela de alteração:")
            for aula in resultado.aulas_fora_da_janela:
                print(f"  - {_formatar_aula(aula)}")
        else:
            print("Nenhuma alternativa satisfaz as restrições obrigatórias.")
        return 0

    print(f"Soluções: {len(resultado.solucoes)}")
    for indice, solucao in enumerate(resultado.solucoes, start=1):
        print(
            f"\nSolução {indice}: "
            f"{solucao.quantidade_de_alteracoes} alterações, "
            f"{len(solucao.professores_afetados)} professores afetados, "
            f"{solucao.quantidade_de_aulas_deslocadas} aulas deslocadas, "
            f"{solucao.janelas_criadas} janelas criadas"
        )
        print(
            "  Professores afetados: "
            + ", ".join(sorted(solucao.professores_afetados))
        )
        alteradas = [
            (base, proposta)
            for base, proposta in zip(grade_base.aulas, solucao.atribuicoes)
            if (proposta.id_professor, proposta.dia, proposta.periodo)
            != (base.id_professor, base.dia, base.periodo)
        ]
        if not alteradas:
            print("  Nenhuma aula alterada.")
            continue
        print("  Aulas alteradas:")
        for base, proposta in alteradas:
            print(f"    {_formatar_aula(base)} -> {_formatar_aula(proposta)}")
    return 0


def _formatar_aula(aula) -> str:
    dia = NOMES_DOS_DIAS.get(aula.dia, str(aula.dia))
    return (
        f"{aula.id_turma} {aula.id_disciplina} "
        f"{dia} P{aula.periodo} ({aula.id_professor})"
    )


if __name__ == "__main__":
    raise SystemExit(main())
