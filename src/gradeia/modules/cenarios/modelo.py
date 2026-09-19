from dataclasses import dataclass


JANELA_DE_ALTERACAO = "JANELA_DE_ALTERACAO"
MANHA = "MANHA"
TARDE = "TARDE"
NOITE = "NOITE"
FUNDAMENTAL = "FUNDAMENTAL"
MEDIO = "MEDIO"
TURNOS_VALIDOS = frozenset({MANHA, TARDE, NOITE})
ETAPAS_VALIDAS = frozenset({FUNDAMENTAL, MEDIO})
PERIODOS_POR_ETAPA = {FUNDAMENTAL: 5, MEDIO: 6}


@dataclass(frozen=True)
class AtribuicaoDeAula:
    id_professor: str
    id_disciplina: str
    id_turma: str
    dia: int
    periodo: int
    turno: str | None = None


@dataclass(frozen=True)
class Turma:
    id_turma: str
    turno: str
    etapa: str

    @property
    def teto_de_periodos(self) -> int:
        return PERIODOS_POR_ETAPA[self.etapa]


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
    detalhes_das_turmas: tuple[Turma, ...] = ()

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

    def perfil_da_turma(self, id_turma: str) -> Turma:
        for turma in self.detalhes_das_turmas:
            if turma.id_turma == id_turma:
                return turma
        return Turma(id_turma=id_turma, turno=MANHA, etapa=MEDIO)


@dataclass(frozen=True)
class AusenciaDeProfessor:
    id_professor: str
    turno: str
    dias: frozenset[int] = frozenset()


@dataclass(frozen=True)
class RestricaoDeCenario:
    tipo: str
    dias_periodos: frozenset[tuple[int, int]]


@dataclass(frozen=True)
class Cenario:
    ausencia: AusenciaDeProfessor
    restricoes: tuple[RestricaoDeCenario, ...] = ()


@dataclass(frozen=True)
class SolucaoDeCenario:
    atribuicoes: tuple[AtribuicaoDeAula, ...] = ()
    quantidade_de_alteracoes: int = 0
    professores_afetados: frozenset[str] = frozenset()
    quantidade_de_aulas_deslocadas: int = 0
    janelas_criadas: int = 0
