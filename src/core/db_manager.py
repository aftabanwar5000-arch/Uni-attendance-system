import sqlite3
import os
import logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATABASE = os.path.join(BASE_DIR, "data", "university.db")

class DBManager:
    @staticmethod
    def get_connection():
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def setup_database():
        try:
            logging.info(f"Connecting to database at {DATABASE}...")
            with DBManager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    department TEXT,
                    semester TEXT,
                    roll_no TEXT
                )
                """)
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_date ON logs (date)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_department ON logs (department)")
                
                # Try to add roll_no column if the table already existed without it
                try:
                    cursor.execute("ALTER TABLE logs ADD COLUMN roll_no TEXT")
                except sqlite3.OperationalError:
                    pass # Column already exists
                    
                conn.commit()
                logging.info("Database and tables initialized successfully.")
        except sqlite3.Error as e:
            logging.error(f"Database setup error: {e}")

    @staticmethod
    def log_attendance(name, status, current_time, department, semester, roll_no=""):
        try:
            with DBManager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO logs 
                    (name, status, date, time, department, semester, roll_no) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (name, status,
                     str(current_time.date()),
                     current_time.strftime("%H:%M:%S"),
                     department,
                     semester,
                     roll_no)
                )
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Database logging error: {e}")
