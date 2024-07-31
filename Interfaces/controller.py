from abc import ABC, abstractmethod

class IController(ABC):
    @abstractmethod
    def authenticateUser(self, username: str, password: str) -> bool: pass

    @abstractmethod
    def evaluateExpression(self, expression: str) -> float: pass

    @abstractmethod
    def plotGraph(self, function: str) -> any: pass

    @abstractmethod
    def performSymbolicComputation(self, expression: str) -> str: pass

    @abstractmethod
    def manageProfile(self, userId: int) -> any: pass

    @abstractmethod
    def exportResults(self, format: str) -> any: pass

    @abstractmethod
    def getComputationHistory(self) -> list: pass
