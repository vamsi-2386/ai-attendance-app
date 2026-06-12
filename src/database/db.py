from src.database.config import get_db_connection
import bcrypt
import json
import sqlite3
import random
import string

def hash_pass(pwd):
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()

def check_pass(pwd, hashed):
    return bcrypt.checkpw(pwd.encode(), hashed.encode())

def generate_invite_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

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
        # Generate unique code
        while True:
            code = generate_invite_code()
            cursor.execute("SELECT id FROM companys WHERE company_invite_code = ?", (code,))
            if cursor.fetchone() is None:
                break
        
        cursor.execute("INSERT INTO companys (username, password, name, company_invite_code) VALUES (?, ?, ?, ?)", 
                       (username, hash_pass(password), name, code))
        conn.commit()
        return [{"username": username, "name": name, "company_invite_code": code}]
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

def get_company_by_invite_code(code):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM companys WHERE company_invite_code = ?", (code,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def get_company_by_id(company_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM companys WHERE id = ?", (company_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def get_all_employees_for_company(company_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees WHERE company_id = ?", (company_id,))
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

def create_employee(employee_code, new_name, company_id, face_embedding=None, voice_embedding=None):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        f_emb_str = json.dumps(face_embedding) if face_embedding else None
        v_emb_str = json.dumps(voice_embedding) if voice_embedding else None
        cursor.execute("INSERT INTO employees (employee_code, name, face_embedding, voice_embedding, company_id) VALUES (?, ?, ?, ?, ?)", 
                       (employee_code, new_name, f_emb_str, v_emb_str, company_id))
        emp_id = cursor.lastrowid
        
        # Auto-enroll in all existing company projects
        cursor.execute("SELECT subject_id FROM subjects WHERE company_id = ?", (company_id,))
        subjects = cursor.fetchall()
        for sub in subjects:
            cursor.execute("INSERT OR IGNORE INTO project_employees (employee_id, subject_id) VALUES (?, ?)", (emp_id, sub['subject_id']))
            
        conn.commit()
        return [{"employee_id": emp_id, "employee_code": employee_code, "name": new_name, "company_id": company_id}]
    finally:
        conn.close()

def assign_employee_to_project(employee_id, subject_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO project_employees (employee_id, subject_id) VALUES (?, ?)", (employee_id, subject_id))
        conn.commit()
    finally:
        conn.close()

def get_enrolled_employees_for_subject(subject_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.* FROM employees e
            JOIN project_employees pe ON e.employee_id = pe.employee_id
            WHERE pe.subject_id = ?
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

def create_subject(subject_code, name, section, company_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO subjects (subject_code, name, section, company_id) VALUES (?, ?, ?, ?)",
                       (subject_code, name, section, company_id))
        sub_id = cursor.lastrowid
        
        # Auto-enroll all existing company employees into this new project
        cursor.execute("SELECT employee_id FROM employees WHERE company_id = ?", (company_id,))
        employees = cursor.fetchall()
        for emp in employees:
            cursor.execute("INSERT OR IGNORE INTO project_employees (employee_id, subject_id) VALUES (?, ?)", (emp['employee_id'], sub_id))
            
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
            (SELECT COUNT(*) FROM employees e WHERE e.company_id = s.company_id) as total_employees
            FROM subjects s WHERE s.company_id = ?
        """, (company_id,))
        subjects = [dict(row) for row in cursor.fetchall()]
        
        for sub in subjects:
            cursor.execute("SELECT COUNT(DISTINCT timestamp) as total_classes FROM attendance_logs WHERE subject_id = ?", (sub['subject_id'],))
            sub['total_classes'] = cursor.fetchone()['total_classes']
            
        return subjects
    finally:
        conn.close()

def get_subjects_for_employee(employee_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.* FROM subjects s
            JOIN project_employees pe ON s.subject_id = pe.subject_id
            WHERE pe.employee_id = ?
        """, (employee_id,))
        subjects = [dict(row) for row in cursor.fetchall()]
        
        for sub in subjects:
            cursor.execute("SELECT COUNT(DISTINCT timestamp) as total_classes FROM attendance_logs WHERE subject_id = ?", (sub['subject_id'],))
            sub['total_classes'] = cursor.fetchone()['total_classes']
            
        return subjects
    finally:
        conn.close()

def get_employee_attendance(employee_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.*, s.name as subject_name 
            FROM attendance_logs a 
            JOIN subjects s ON a.subject_id = s.subject_id
            WHERE a.employee_id = ?
        """, (employee_id,))
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
            SELECT a.*, s.subject_code, s.name, s.section, e.name as employee_name
            FROM attendance_logs a
            JOIN subjects s ON a.subject_id = s.subject_id
            JOIN employees e ON a.employee_id = e.employee_id
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

def update_company_location(company_id, lat, lng, radius):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE companys 
            SET office_lat = ?, office_lng = ?, office_radius = ?
            WHERE id = ?
        """, (lat, lng, radius, company_id))
        conn.commit()
    finally:
        conn.close()

def employee_gps_checkin(employee_id, subject_id, timestamp, lat, lng, status):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO attendance_logs (employee_id, subject_id, timestamp, is_present, latitude, longitude, location_status) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (employee_id, subject_id, timestamp, True, lat, lng, status))
        conn.commit()
    finally:
        conn.close()

def employee_gps_checkout(attendance_id, checkout_time):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE attendance_logs 
            SET checkout_time = ?
            WHERE id = ?
        """, (checkout_time, attendance_id))
        conn.commit()
    finally:
        conn.close()
