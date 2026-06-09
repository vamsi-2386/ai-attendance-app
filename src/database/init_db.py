import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'app.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.executescript('''
    CREATE TABLE IF NOT EXISTS companys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        name TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS employees (
        employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        face_embedding TEXT,
        voice_embedding TEXT
    );

    CREATE TABLE IF NOT EXISTS subjects (
        subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_code TEXT NOT NULL,
        name TEXT NOT NULL,
        section TEXT,
        company_id INTEGER NOT NULL,
        FOREIGN KEY (company_id) REFERENCES companys(id)
    );

    CREATE TABLE IF NOT EXISTS subject_employees (
        subject_id INTEGER NOT NULL,
        employee_id INTEGER NOT NULL,
        PRIMARY KEY (subject_id, employee_id),
        FOREIGN KEY (subject_id) REFERENCES subjects(subject_id),
        FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
    );

    CREATE TABLE IF NOT EXISTS attendance_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL,
        subject_id INTEGER NOT NULL,
        timestamp TEXT NOT NULL,
        is_present BOOLEAN NOT NULL,
        FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
        FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
    );
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
