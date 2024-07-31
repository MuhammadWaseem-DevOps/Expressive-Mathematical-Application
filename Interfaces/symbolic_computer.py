from abc import ABC, abstractmethod

class ISymbolicComputer(ABC):
    @abstractmethod
    def simplify(self, expression: str) -> str: pass

    @abstractmethod
    def solve(self, equation: str) -> list: pass
