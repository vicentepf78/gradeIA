from dataclasses import dataclass


JANELA_DE_ALTERACAO = "JANELA_DE_ALTERACAO"


@dataclass(frozen=True)
class AtribuicaoDeAula:
    id_professor: str
    id_disciplina: str
    id_turma: str
    dia: int
    periodo: int


@dataclass(frozen=True)
class Professor:
    id_professor: str
    disciplinas_habilitadas: frozenset[str]
    disponibilidade: frozenset[tuple[int, int]]


@dataclass(frozen=True)
class GradeBase:
    professores: frozenset[str]
    disciplinas: frozenset[str]
    turmas: frozenset[str]
    dias: frozenset[int]
    periodos: frozenset[int]
    aulas: tuple[AtribuicaoDeAula, ...]
    detalhes_dos_professores: tuple[Professor, ...] = ()

    def perfil_do_professor(self, id_professor: str) -> Professor:
        for perfil in self.detalhes_dos_professores:
            if perfil.id_professor == id_professor:
                return perfil
        return Professor(
            id_professor=id_professor,
            disciplinas_habilitadas=self.disciplinas,
            disponibilidade=frozenset(
                (dia, periodo) for dia in self.dias for periodo in self.periodos
            ),
        )


@dataclass(frozen=True)
class AusenciaDeProfessor:
    id_professor: str
    dias_periodos: frozenset[tuple[int, int]]


@dataclass(frozen=True)
class RestricaoDeCenario:
    tipo: str
    dias_periodos: frozenset[tuple[int, int]]


@dataclass(frozen=True)
class Cenario:
    ausencia: AusenciaDeProfessor
    restricoes: tuple[RestricaoDeCenario, ...]


@dataclass(frozen=True)
class SolucaoDeCenario:
    atribuicoes: tuple[AtribuicaoDeAula, ...] = ()
