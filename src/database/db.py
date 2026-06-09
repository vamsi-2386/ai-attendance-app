from src.database.config import get_db_connection
import bcrypt
import json
import sqlite3
import sqlite3

def hash_pass(pwd):
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()

def check_pass(pwd, hashed):
    return bcrypt.checkpw(pwd.encode(), hashed.encode())

def check_company_exists(username):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM companys WHERE username = ?", (username,))
        row = cursor.fetchone()
        return row is not None
    finally:
        conn.close()

def create_company(username, password, name):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO companys (username, password, name) VALUES (?, ?, ?)", 
                       (username, hash_pass(password), name))
        conn.commit()
        return [{"username": username, "name": name}]
    finally:
        conn.close()

def company_login(username, password):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM companys WHERE username = ?", (username,))
        row = cursor.fetchone()
        if row:
            company = dict(row)
            if check_pass(password, company['password']):
                company['company_id'] = company['id'] # Map for app compatibility
                return company
        return None
    finally:
        conn.close()

def get_all_employees():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees")
        rows = cursor.fetchall()
        results = []
        for r in rows:
            d = dict(r)
            d['face_embedding'] = json.loads(d['face_embedding']) if d['face_embedding'] else None
            d['voice_embedding'] = json.loads(d['voice_embedding']) if d['voice_embedding'] else None
            results.append(d)
        return results
    finally:
        conn.close()

def create_employee(new_name, face_embedding=None, voice_embedding=None):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        f_emb_str = json.dumps(face_embedding) if face_embedding else None
        v_emb_str = json.dumps(voice_embedding) if voice_embedding else None
        cursor.execute("INSERT INTO employees (name, face_embedding, voice_embedding) VALUES (?, ?, ?)", 
                       (new_name, f_emb_str, v_emb_str))
        emp_id = cursor.lastrowid
        conn.commit()
        return [{"employee_id": emp_id, "name": new_name}]
    finally:
        conn.close()

def create_subject(subject_code, name, section, company_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO subjects (subject_code, name, section, company_id) VALUES (?, ?, ?, ?)",
                       (subject_code, name, section, company_id))
        conn.commit()
        return [{"subject_code": subject_code, "name": name}]
    finally:
        conn.close()

def get_company_subjects(company_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.*, 
            (SELECT COUNT(*) FROM subject_employees se WHERE se.subject_id = s.subject_id) as total_employees
            FROM subjects s WHERE s.company_id = ?
        """, (company_id,))
        subjects = [dict(row) for row in cursor.fetchall()]
        
        for sub in subjects:
            cursor.execute("SELECT COUNT(DISTINCT timestamp) as total_classes FROM attendance_logs WHERE subject_id = ?", (sub['subject_id'],))
            sub['total_classes'] = cursor.fetchone()['total_classes']
            
        return subjects
    finally:
        conn.close()

def enroll_employee_to_subject(employee_id, subject_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO subject_employees (employee_id, subject_id) VALUES (?, ?)", (employee_id, subject_id))
            conn.commit()
        except sqlite3.IntegrityError:
            pass # Already enrolled
        return [{"employee_id": employee_id, "subject_id": subject_id}]
    finally:
        conn.close()

def unenroll_employee_to_subject(employee_id, subject_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM subject_employees WHERE employee_id = ? AND subject_id = ?", (employee_id, subject_id))
        conn.commit()
        return []
    finally:
        conn.close()

def get_employee_subjects(employee_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT se.*, s.subject_id as s_id, s.subject_code, s.name, s.section, s.company_id 
            FROM subject_employees se 
            JOIN subjects s ON se.subject_id = s.subject_id 
            WHERE se.employee_id = ?
        """, (employee_id,))
        rows = cursor.fetchall()
        results = []
        for r in rows:
            d = dict(r)
            d['subjects'] = {
                'subject_id': d['s_id'],
                'subject_code': d['subject_code'],
                'name': d['name'],
                'section': d['section'],
                'company_id': d['company_id']
            }
            results.append(d)
        return results
    finally:
        conn.close()

def get_employee_attendance(employee_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM attendance_logs WHERE employee_id = ?", (employee_id,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def create_attendance(logs):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        for log in logs:
            cursor.execute("INSERT INTO attendance_logs (employee_id, subject_id, timestamp, is_present) VALUES (?, ?, ?, ?)",
                           (log['employee_id'], log['subject_id'], log['timestamp'], log['is_present']))
        conn.commit()
        return logs
    finally:
        conn.close()

def get_attendance_for_company(company_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.*, s.subject_code, s.name, s.section
            FROM attendance_logs a
            JOIN subjects s ON a.subject_id = s.subject_id
            WHERE s.company_id = ?
        """, (company_id,))
        rows = cursor.fetchall()
        results = []
        for r in rows:
            d = dict(r)
            d['subjects'] = {
                'subject_code': d['subject_code'],
                'name': d['name'],
                'section': d['section']
            }
            results.append(d)
        return results
    finally:
        conn.close()


def get_subject_by_code(subject_code):
    """Look up a subject by its join code. Returns dict or None."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM subjects WHERE subject_code = ?", (subject_code,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def is_employee_enrolled(employee_id, subject_id):
    """Return True if the employee is already enrolled in the given subject."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM subject_employees WHERE employee_id=? AND subject_id=?",
            (employee_id, subject_id)
        )
        return cursor.fetchone() is not None
    finally:
        conn.close()


def get_enrolled_employees_for_subject(subject_id):
    """Return list of employee dicts (with parsed embeddings) for a subject."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.*
            FROM employees e
            JOIN subject_employees se ON e.employee_id = se.employee_id
            WHERE se.subject_id = ?
        """, (subject_id,))
        rows = cursor.fetchall()
        results = []
        for r in rows:
            d = dict(r)
            d['face_embedding'] = json.loads(d['face_embedding']) if d['face_embedding'] else None
            d['voice_embedding'] = json.loads(d['voice_embedding']) if d['voice_embedding'] else None
            results.append(d)
        return results
    finally:
        conn.close()
