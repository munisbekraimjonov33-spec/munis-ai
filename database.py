import sqlite3

class Database:
    def __init__(self, path_to_db="main.db"):
        self.path_to_db = path_to_db

    @property
    def connection(self):
        return sqlite3.connect(self.path_to_db)

    def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = ()
        connection = self.connection
        # connection.set_trace_callback(logger)
        cursor = connection.cursor()
        data = None
        cursor.execute(sql, parameters)

        if commit:
            connection.commit()
        if fetchone:
            data = cursor.fetchone()
        if fetchall:
            data = cursor.fetchall()
        connection.close()
        return data

    def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            full_name VARCHAR(255),
            username VARCHAR(255),
            join_date DATE,
            is_pro BOOLEAN DEFAULT FALSE,
            daily_requests INTEGER DEFAULT 0,
            last_request_date DATE
        );
        """
        self.execute(sql, commit=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ?" for item in parameters
        ])
        return sql, tuple(parameters.values())

    def add_user(self, id: int, full_name: str, username: str = None, join_date: str = None):
        sql = """
        INSERT OR IGNORE INTO users(id, full_name, username, join_date, daily_requests, last_request_date) VALUES(?, ?, ?, ?, 0, ?)
        """
        self.execute(sql, parameters=(id, full_name, username, join_date, join_date), commit=True)

    def select_user(self, **kwargs):
        sql = "SELECT * FROM users WHERE "
        sql, parameters = self.format_args(sql, kwargs)
        return self.execute(sql, parameters=parameters, fetchone=True)

    def count_users(self):
        return self.execute("SELECT COUNT(*) FROM users;", fetchone=True)

    def update_user_daily_limit(self, id: int, daily_requests: int, last_request_date: str):
        sql = """
        UPDATE users SET daily_requests=?, last_request_date=? WHERE id=?
        """
        self.execute(sql, parameters=(daily_requests, last_request_date, id), commit=True)

    def set_pro_status(self, id: int, is_pro: bool):
        sql = """
        UPDATE users SET is_pro=? WHERE id=?
        """
        self.execute(sql, parameters=(is_pro, id), commit=True)

    def get_all_users(self):
        sql = "SELECT id, full_name FROM users"
        return self.execute(sql, fetchall=True)
