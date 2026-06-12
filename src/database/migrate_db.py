import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'app.db')

def migrate():
    print(f"Connecting to {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Add columns to companys table
        print("Adding office location columns to companys table...")
        cursor.execute("ALTER TABLE companys ADD COLUMN office_lat REAL;")
        cursor.execute("ALTER TABLE companys ADD COLUMN office_lng REAL;")
        cursor.execute("ALTER TABLE companys ADD COLUMN office_radius INTEGER DEFAULT 100;")
    except sqlite3.OperationalError as e:
        print(f"Column might already exist in companys: {e}")

    try:
        # Add columns to attendance_logs table
        print("Adding GPS columns to attendance_logs table...")
        cursor.execute("ALTER TABLE attendance_logs ADD COLUMN checkout_time TEXT;")
        cursor.execute("ALTER TABLE attendance_logs ADD COLUMN latitude REAL;")
        cursor.execute("ALTER TABLE attendance_logs ADD COLUMN longitude REAL;")
        cursor.execute("ALTER TABLE attendance_logs ADD COLUMN location_status TEXT;")
    except sqlite3.OperationalError as e:
        print(f"Column might already exist in attendance_logs: {e}")

    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == '__main__':
    migrate()
