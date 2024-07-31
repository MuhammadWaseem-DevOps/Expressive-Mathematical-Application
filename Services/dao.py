from Interfaces.dao import IDataAccessObject

class SQLiteDataAccessObject(IDataAccessObject):
    def __init__(self, db):
        self.db = db

    def insert(self, table: str, data: dict) -> int:
        # Implement insert logic
        return 0

    def update(self, table: str, id: int, data: dict) -> bool:
        # Implement update logic
        return True

    def delete(self, table: str, id: int) -> bool:
        # Implement delete logic
        return True

    def select(self, table: str, condition: str) -> list:
        # Implement select logic
        return []
