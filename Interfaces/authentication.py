from abc import ABC, abstractmethod

class IAuthenticationService(ABC):
    @abstractmethod
    def authenticateUser(self, username: str, password: str) -> bool: pass

    @abstractmethod
    def createUser(self, username: str, password: str, email: str) -> any: pass
