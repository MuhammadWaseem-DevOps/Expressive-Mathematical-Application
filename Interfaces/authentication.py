from abc import ABC, abstractmethod

class IAuthenticationService(ABC):
    @abstractmethod
    def authenticate_user(self, username: str, password: str) -> bool: pass

    @abstractmethod
    def create_user(self, username: str, password: str, email: str) -> any: pass
