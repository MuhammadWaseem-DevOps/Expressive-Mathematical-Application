from Interfaces.dao import IDataAccessObject
import sqlite3
import os

class SQLiteDataAccessObject(IDataAccessObject):
    def __init__(self, db_name: str = 'example.db'):
        self.db_name = db_name
        self.connection = self._connect()
        self._create_tables()

    def _connect(self):
        """Establishes a database connection."""
        return sqlite3.connect(self.db_name)
    def _create_tables(self):
        """Creates necessary tables if they do not exist."""
        cursor = self.connection.cursor()

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
            expression TEXT,
            result TEXT,
            computation_type TEXT,
            timestamp DATETIME,
            graph_data BLOB,
            symbolic_steps JSON,
            FOREIGN KEY (user_id) REFERENCES USER (user_id)
        )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS EXPRESSION_EVALUATOR (
            evaluator_id INTEGER PRIMARY KEY,
            expression_type TEXT,
            evaluation_method TEXT
        )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS GRAPHICAL_FUNCTION (
            graph_id INTEGER PRIMARY KEY,
            history_id INTEGER NOT NULL,
            function TEXT,
            plot_settings JSON,
            FOREIGN KEY (history_id) REFERENCES COMPUTATION_HISTORY (history_id)
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


    def insert(self, table: str, data: dict) -> int:
        """Inserts a record into the specified table."""
        keys = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        sql = f"INSERT INTO {table} ({keys}) VALUES ({placeholders})"
        cursor = self.connection.cursor()
        cursor.execute(sql, tuple(data.values()))
        self.connection.commit()
        return cursor.lastrowid

    def update(self, table: str, id: int, data: dict) -> bool:
        """Updates a record in the specified table."""
        set_clause = ', '.join([f"{key} = ?" for key in data])
        sql = f"UPDATE {table} SET {set_clause} WHERE {table}_id = ?"
        cursor = self.connection.cursor()
        cursor.execute(sql, tuple(data.values()) + (id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def delete(self, table: str, id: int) -> bool:
        """Deletes a record from the specified table."""
        sql = f"DELETE FROM {table} WHERE {table}_id = ?"
        cursor = self.connection.cursor()
        cursor.execute(sql, (id,))
        self.connection.commit()
        return cursor.rowcount > 0

    def select(self, table: str, condition: str = "") -> list:
        """Selects records from the specified table based on a condition."""
        sql = f"SELECT * FROM {table}"
        if condition:
            sql += f" WHERE {condition}"
        cursor = self.connection.cursor()
        cursor.execute(sql)
        return cursor.fetchall()

    def close(self):
        """Closes the database connection."""
        self.connection.close()
