from abc import ABC, abstractmethod

from gradeia.modules.cenarios import Cenario, GradeBase, ResultadoDaSimulacao


class SchedulingEngine(ABC):
    @abstractmethod
    def simular(self, grade_base: GradeBase, cenario: Cenario) -> ResultadoDaSimulacao:
        raise NotImplementedError
