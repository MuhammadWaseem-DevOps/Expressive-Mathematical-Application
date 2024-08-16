from abc import ABC, abstractmethod
from typing import List, Any

class ISymbolicComputer:
    def tokenize(self, expression: str) -> List[Any]:
        raise NotImplementedError

    def build_tree(self, tokens: List[Any]) -> Any:
        raise NotImplementedError

    def evaluate_node(self, node: Any) -> Any:
        raise NotImplementedError

    def differentiate_tree(self, node: Any, variable: str) -> Any:
        raise NotImplementedError

    def integrate_tree(self, node: Any, variable: str) -> Any:
        raise NotImplementedError
    @abstractmethod
    def simplify(self, expression: str) -> str: pass

    @abstractmethod
    def solve(self, equation: str) -> list: pass
