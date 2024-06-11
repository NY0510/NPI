import sqlite3
import os

DB_NAME = os.path.join("app", 'database', 'db.sqlite3')

class Database:
    def __init__(self, db_name = DB_NAME):
        db_path = os.path.join(os.getcwd(), db_name)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row 
        print(f"Connected to database {db_name} successfully.")

    def execute(self, query, params=None):
        cursor = self.conn.cursor()
        if params is not None:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        self.conn.commit()
        return cursor
        
    def fetchall(self, query, params=None):
        cursor = self.execute(query, params)
        return cursor.fetchall()

    def fetchone(self, query, params=None):
        cursor = self.execute(query, params)
        return cursor.fetchone()

    def close(self):
        self.conn.close()


