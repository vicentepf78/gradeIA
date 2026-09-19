import json
from pathlib import Path

from gradeia.modules.cenarios.modelo import (
    JANELA_DE_ALTERACAO,
    MANHA,
    MEDIO,
    AtribuicaoDeAula,
    AusenciaDeProfessor,
    Cenario,
    GradeBase,
    Professor,
    RestricaoDeCenario,
    Turma,
)

DATASET_PADRAO = Path("dados/grade-basica.json")


def carregar_simulacao(caminho: Path) -> tuple[GradeBase, Cenario]:
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    dias = frozenset(dados["dias"])
    periodos = frozenset(dados["periodos"])
    disciplinas = frozenset(dados["disciplinas"])
    turmas = tuple(_turma(item) for item in dados["turmas"])
    professores = tuple(
        _professor(item, dias, periodos) for item in dados["professores"]
    )
    aulas = tuple(_aula(item) for item in dados["aulas"])
    grade_base = GradeBase(
        professores=frozenset(perfil.id_professor for perfil in professores),
        disciplinas=disciplinas,
        turmas=frozenset(turma.id_turma for turma in turmas),
        dias=dias,
        periodos=periodos,
        aulas=aulas,
        detalhes_dos_professores=professores,
        detalhes_das_turmas=turmas,
    )
    return grade_base, _cenario(dados["cenario"])


def _pares(valor: object, dias: frozenset[int], periodos: frozenset[int]) -> frozenset[tuple[int, int]]:
    if valor == "todos":
        return frozenset((dia, periodo) for dia in dias for periodo in periodos)
    if not isinstance(valor, list):
        raise ValueError("disponibilidade ou janela deve ser 'todos' ou lista de pares")
    return frozenset((int(par[0]), int(par[1])) for par in valor)


def _turma(item: dict | str) -> Turma:
    if isinstance(item, str):
        return Turma(id_turma=item, turno=MANHA, etapa=MEDIO)
    return Turma(
        id_turma=item["idTurma"],
        turno=item["turno"],
        etapa=item["etapa"],
    )


def _professor(
    item: dict,
    dias: frozenset[int],
    periodos: frozenset[int],
) -> Professor:
    return Professor(
        id_professor=item["idProfessor"],
        disciplinas_habilitadas=frozenset(item["disciplinasHabilitadas"]),
        disponibilidade=_pares(item.get("disponibilidade", "todos"), dias, periodos),
    )


def _aula(item: dict) -> AtribuicaoDeAula:
    return AtribuicaoDeAula(
        id_professor=item["idProfessor"],
        id_disciplina=item["idDisciplina"],
        id_turma=item["idTurma"],
        dia=int(item["dia"]),
        periodo=int(item["periodo"]),
        turno=item.get("turno"),
    )


def _cenario(item: dict) -> Cenario:
    ausencia = item["ausencia"]
    restricoes = tuple(
        RestricaoDeCenario(
            tipo=restricao.get("tipo", JANELA_DE_ALTERACAO),
            dias_periodos=frozenset(
                (int(par[0]), int(par[1])) for par in restricao["diasPeriodos"]
            ),
        )
        for restricao in item.get("restricoes", [])
    )
    dias = ausencia.get("dias") or []
    return Cenario(
        ausencia=AusenciaDeProfessor(
            id_professor=ausencia["idProfessor"],
            turno=ausencia["turno"],
            dias=frozenset(int(dia) for dia in dias),
        ),
        restricoes=restricoes,
    )
