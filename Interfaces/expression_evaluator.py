from abc import ABC, abstractmethod

class IExpressionEvaluator(ABC):
    @abstractmethod
    def evaluate(self, expression: str) -> float: pass
