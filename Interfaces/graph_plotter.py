from abc import ABC, abstractmethod

class IGraphPlotter(ABC):
    @abstractmethod
    def plotFunction(self, function: str) -> any: pass

    @abstractmethod
    def customizePlot(self, options: dict): pass
