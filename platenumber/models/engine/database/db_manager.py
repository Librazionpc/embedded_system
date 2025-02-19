import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name):
        self.db_name = db_name
        
    def connect(self):
        return sqlite3.connect(self.db_name)
    
    def execute_query(self, query, params=(), commit=False):
        try:
            with self.connect() as db_conn:
                db_cursor = db_conn.cursor()
                db_cursor.execute(query, params)
                if commit:
                    db_conn.commit()
                return db_cursor
        except sqlite3.InternalError as e:
            print(f"IntegrityError: {e}")
            return False
        except sqlite3.Error as e:
            print(f"SQLite Error: {e}")
            return False
        except Exception as e:
            print(f"Code Error: {e}")
            return False
    
    def fetch(self, query, params=()):
        try:
            with self.connect() as db_conn:
                db_cursor = db_conn.cursor()
                db_cursor.execute(query, params)
                results = db_cursor.fetchall()
                return results
        except sqlite3.InternalError as e:
            print(f"IntegrityError: {e}")
            return False
        except sqlite3.Error as e:
            print(f"SQLite Error: {e}")
            return False
        except Exception as e:
            print(f"Code Error: {e}")
            return False

    def record_exist(self, table, column, value):
        query = f"SELECT 1 FROM {table} WHERE {column} = ?"
        cursor = self.execute_query(query, (value,))
        return cursor.fetchone() is not None