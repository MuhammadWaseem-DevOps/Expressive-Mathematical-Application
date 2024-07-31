from abc import ABC, abstractmethod

class IErrorHandler(ABC):
    @abstractmethod
    def handleError(self, error: Exception) -> str: pass

    @abstractmethod
    def logError(self, error: Exception): pass

    @abstractmethod
    def validateInput(self, input: str) -> bool: pass
    
