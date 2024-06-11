import sqlite3
import os

class Database:
    def __init__(self, db_name):
        db_path = os.path.join(os.getcwd(), db_name)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row 
        print(f"Connected to database {db_name} successfully.")

    def execute(self, query, params=None):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor

    def fetch_all(self, query, params=None):
        cursor = self.execute_query(query, params)
        return cursor.fetchall()

    def fetch_one(self, query, params=None):
        cursor = self.execute_query(query, params)
        return cursor.fetchone()

    def close(self):
        self.conn.close()

db = Database(os.path.join('app', 'database', 'db.sqlite3'))
