from abc import ABC, abstractmethod

class IDataAccessObject(ABC):
    @abstractmethod
    def insert(self, table: str, data: dict) -> int: pass

    @abstractmethod
    def update(self, table: str, id: int, data: dict) -> bool: pass

    @abstractmethod
    def delete(self, table: str, id: int) -> bool: pass

    @abstractmethod
    def select(self, table: str, condition: str) -> list: pass
