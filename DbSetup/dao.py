import sqlite3
import json
import datetime
from Interfaces.dao import IDataAccessObject

class SQLiteDataAccessObject(IDataAccessObject):
    def __init__(self, db_name: str = 'example.db'):
        self.db_name = db_name
        self.connection = self._connect()
        self._create_tables()

    def _connect(self):
        return sqlite3.connect(self.db_name)

    def _create_tables(self):
        cursor = self.connection.cursor()

        # Drop the existing GRAPHICAL_FUNCTION table if it exists
        cursor.execute('''DROP TABLE IF EXISTS GRAPHICAL_FUNCTION''')

        # Recreate all the necessary tables with the correct structure
        cursor.execute('''CREATE TABLE IF NOT EXISTS USER (
            user_id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            first_name TEXT,
            last_name TEXT,
            profile_picture BLOB,
            created_at DATETIME NOT NULL,
            last_login DATETIME
        )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS PROFILE (
            profile_id INTEGER PRIMARY KEY,
            user_id INTEGER UNIQUE NOT NULL,
            full_name TEXT,
            preferences JSON,
            last_updated DATETIME,
            FOREIGN KEY (user_id) REFERENCES USER (user_id)
        )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS COMPUTATION_HISTORY (
            history_id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            expression TEXT NOT NULL,
            result TEXT,
            computation_type TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            symbolic_steps JSON,
            graph_data_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES USER (user_id),
            FOREIGN KEY (graph_data_id) REFERENCES GRAPHICAL_FUNCTION (graph_id)
        )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS GRAPHICAL_FUNCTION (
            graph_id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            function TEXT NOT NULL,
            x_min REAL NOT NULL,
            x_max REAL NOT NULL,
            timestamp DATETIME NOT NULL,
            image BLOB,
            FOREIGN KEY (user_id) REFERENCES USER (user_id)
        )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS ERROR_LOG (
            error_id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            error_message TEXT,
            error_type TEXT,
            timestamp DATETIME,
            FOREIGN KEY (user_id) REFERENCES USER (user_id)
        )''')

        self.connection.commit()

    def insert_computation_history(self, user_id, expression, result, computation_type, symbolic_steps, graph_data_id=None):
        data = {
            'user_id': user_id,
            'expression': expression,
            'result': result,
            'computation_type': computation_type,
            'timestamp': datetime.datetime.now().isoformat(),
            'symbolic_steps': json.dumps(symbolic_steps),
            'graph_data_id': graph_data_id
        }
        return self.insert('COMPUTATION_HISTORY', data)

    def insert(self, table: str, data: dict) -> int:
        # Ensure user_id is not None before inserting
        if 'user_id' in data and data['user_id'] is None:
            raise ValueError(f"Cannot insert into {table}: 'user_id' is None.")

        keys = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        sql = f"INSERT INTO {table} ({keys}) VALUES ({placeholders})"
        cursor = self.connection.cursor()
        cursor.execute(sql, tuple(data.values()))
        self.connection.commit()
        return cursor.lastrowid

    def update(self, table: str, id: int, data: dict) -> bool:
        set_clause = ', '.join([f"{key} = ?" for key in data])
        sql = f"UPDATE {table} SET {set_clause} WHERE {table}_id = ?"
        cursor = self.connection.cursor()
        cursor.execute(sql, tuple(data.values()) + (id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def delete(self, table: str, id: int) -> bool:
        sql = f"DELETE FROM {table} WHERE {table}_id = ?"
        cursor = self.connection.cursor()
        cursor.execute(sql, (id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def select(self, table: str, condition: str = "") -> list:
        sql = f"SELECT * FROM {table}"
        if condition:
            sql += f" WHERE {condition}"
        cursor = self.connection.cursor()
        cursor.execute(sql)
        return cursor.fetchall()

    def get_computation_history(self, user_id):
        return self.select('COMPUTATION_HISTORY', f"user_id = {user_id}")

    def close(self):
        self.connection.close()
