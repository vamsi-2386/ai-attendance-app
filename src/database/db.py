from src.database.supabase_client import supabase
import bcrypt
import random
import string

def hash_pass(pwd):
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()

def check_pass(pwd, hashed):
    return bcrypt.checkpw(pwd.encode(), hashed.encode())

def generate_invite_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def check_company_exists(username):
    response = supabase.table('companys').select('username').eq('username', username).execute()
    return len(response.data) > 0

def create_company(username, password, name):
    while True:
        code = generate_invite_code()
        res = supabase.table('companys').select('id').eq('company_invite_code', code).execute()
        if len(res.data) == 0:
            break
            
    response = supabase.table('companys').insert({
        'username': username,
        'password': hash_pass(password),
        'name': name,
        'company_invite_code': code
    }).execute()
    return response.data

def company_login(username, password):
    response = supabase.table('companys').select('*').eq('username', username).execute()
    if response.data:
        company = response.data[0]
        if check_pass(password, company['password']):
            company['company_id'] = company['id'] # Map for app compatibility
            return company
    return None

def get_company_by_invite_code(code):
    response = supabase.table('companys').select('*').eq('company_invite_code', code).execute()
    return response.data[0] if response.data else None

def get_company_by_id(company_id):
    response = supabase.table('companys').select('*').eq('id', company_id).execute()
    return response.data[0] if response.data else None

def get_all_employees_for_company(company_id):
    response = supabase.table('employees').select('*').eq('company_id', company_id).execute()
    return response.data

def get_all_employees():
    response = supabase.table('employees').select('*').execute()
    return response.data

def create_employee(employee_code, new_name, company_id, face_embedding=None, voice_embedding=None):
    response = supabase.table('employees').insert({
        'employee_code': employee_code,
        'name': new_name,
        'company_id': company_id,
        'face_embedding': face_embedding,
        'voice_embedding': voice_embedding
    }).execute()
    emp_data = response.data[0]
    emp_id = emp_data['employee_id']
    
    # Auto-enroll in all existing company projects
    sub_res = supabase.table('subjects').select('subject_id').eq('company_id', company_id).execute()
    for sub in sub_res.data:
        assign_employee_to_project(emp_id, sub['subject_id'])
        
    return response.data

def assign_employee_to_project(employee_id, subject_id):
    # check if exists
    res = supabase.table('project_employees').select('*').eq('employee_id', employee_id).eq('subject_id', subject_id).execute()
    if not res.data:
        supabase.table('project_employees').insert({
            'employee_id': employee_id,
            'subject_id': subject_id
        }).execute()

def get_enrolled_employees_for_subject(subject_id):
    pe_res = supabase.table('project_employees').select('employee_id').eq('subject_id', subject_id).execute()
    emp_ids = [x['employee_id'] for x in pe_res.data]
    if not emp_ids:
        return []
    
    emp_res = supabase.table('employees').select('*').in_('employee_id', emp_ids).execute()
    return emp_res.data

def create_subject(subject_code, name, section, company_id):
    response = supabase.table('subjects').insert({
        'subject_code': subject_code,
        'name': name,
        'section': section,
        'company_id': company_id
    }).execute()
    sub_data = response.data[0]
    sub_id = sub_data['subject_id']
    
    # Auto-enroll all existing company employees into this new project
    emp_res = supabase.table('employees').select('employee_id').eq('company_id', company_id).execute()
    for emp in emp_res.data:
        assign_employee_to_project(emp['employee_id'], sub_id)
        
    return response.data

import time

def get_company_subjects(company_id):
    for attempt in range(3):
        try:
            sub_res = supabase.table('subjects').select('*').eq('company_id', company_id).execute()
            subjects = sub_res.data
            
            emp_res = supabase.table('employees').select('employee_id').eq('company_id', company_id).execute()
            total_employees = len(emp_res.data)
            
            for sub in subjects:
                sub['total_employees'] = total_employees
                logs_res = supabase.table('attendance_logs').select('timestamp').eq('subject_id', sub['subject_id']).execute()
                unique_classes = len(set(x['timestamp'] for x in logs_res.data))
                sub['total_classes'] = unique_classes
                
            return subjects
        except Exception as e:
            if attempt == 2:
                import streamlit as st
                st.error("📡 Cannot connect to the database. The server may be restarting or your connection dropped. Please refresh the page.")
                st.stop()
            time.sleep(1)

def get_subjects_for_employee(employee_id):
    import time
    for attempt in range(3):
        try:
            pe_res = supabase.table('project_employees').select('subject_id').eq('employee_id', employee_id).execute()
            sub_ids = [x['subject_id'] for x in pe_res.data]
            if not sub_ids:
                return []
                
            sub_res = supabase.table('subjects').select('*').in_('subject_id', sub_ids).execute()
            subjects = sub_res.data
            
            for sub in subjects:
                logs_res = supabase.table('attendance_logs').select('timestamp').eq('subject_id', sub['subject_id']).execute()
                unique_classes = len(set(x['timestamp'] for x in logs_res.data))
                sub['total_classes'] = unique_classes
                
            return subjects
        except Exception as e:
            if attempt == 2:
                import streamlit as st
                st.error("📡 Cannot connect to the database. The server may be restarting or your connection dropped. Please refresh the page.")
                st.stop()
            time.sleep(1)

def get_employee_attendance(employee_id):
    logs_res = supabase.table('attendance_logs').select('*').eq('employee_id', employee_id).execute()
    logs = logs_res.data
    if not logs:
        return []
        
    sub_ids = list(set(log['subject_id'] for log in logs))
    sub_res = supabase.table('subjects').select('subject_id, name').in_('subject_id', sub_ids).execute()
    sub_dict = {x['subject_id']: x['name'] for x in sub_res.data}
    
    for log in logs:
        log['subject_name'] = sub_dict.get(log['subject_id'], 'Unknown Subject')
        
    return logs

def create_attendance(logs):
    if not logs:
        return []
    # Ensure they have all needed fields for Supabase
    supabase.table('attendance_logs').insert(logs).execute()
    return logs

def get_attendance_for_company(company_id):
    # Fetch subjects for this company
    sub_res = supabase.table('subjects').select('*').eq('company_id', company_id).execute()
    subjects = sub_res.data
    if not subjects:
        return []
        
    sub_ids = [sub['subject_id'] for sub in subjects]
    sub_dict = {sub['subject_id']: sub for sub in subjects}
    
    # Fetch logs for these subjects
    logs_res = supabase.table('attendance_logs').select('*').in_('subject_id', sub_ids).execute()
    logs = logs_res.data
    if not logs:
        return []
        
    # Fetch employees to get their names
    emp_ids = list(set(log['employee_id'] for log in logs))
    emp_res = supabase.table('employees').select('employee_id, name').in_('employee_id', emp_ids).execute()
    emp_dict = {emp['employee_id']: emp['name'] for emp in emp_res.data}
    
    results = []
    for log in logs:
        sub = sub_dict.get(log['subject_id'], {})
        emp_name = emp_dict.get(log['employee_id'], 'Unknown')
        log['subjects'] = {
            'subject_code': sub.get('subject_code'),
            'name': sub.get('name'),
            'section': sub.get('section')
        }
        log['employee_name'] = emp_name
        results.append(log)
        
    return results

def get_subject_by_code(subject_code):
    response = supabase.table('subjects').select('*').eq('subject_code', subject_code).execute()
    return response.data[0] if response.data else None

def update_company_location(company_id, lat, lng, radius):
    supabase.table('companys').update({
        'office_lat': lat,
        'office_lng': lng,
        'office_radius': radius
    }).eq('id', company_id).execute()

def employee_gps_checkin(employee_id, subject_id, timestamp, lat, lng, status, is_present=True):
    supabase.table('attendance_logs').insert({
        'employee_id': employee_id,
        'subject_id': subject_id,
        'timestamp': timestamp,
        'is_present': is_present,
        'latitude': lat,
        'longitude': lng,
        'location_status': status
    }).execute()

def employee_gps_checkout(attendance_id, checkout_time):
    supabase.table('attendance_logs').update({
        'checkout_time': checkout_time
    }).eq('id', attendance_id).execute()

def is_employee_enrolled(employee_id, subject_id):
    res = supabase.table('project_employees').select('*').eq('employee_id', employee_id).eq('subject_id', subject_id).execute()
    return len(res.data) > 0

def enroll_employee_to_subject(employee_id, subject_id):
    assign_employee_to_project(employee_id, subject_id)

def unenroll_employee_from_subject(employee_id, subject_id):
    supabase.table('project_employees').delete().eq('employee_id', employee_id).eq('subject_id', subject_id).execute()

def update_employee_designation(employee_id, designation):
    supabase.table('employees').update({'designation': designation}).eq('employee_id', employee_id).execute()

def create_leave_request(employee_id, company_id, start_date, end_date, reason):
    response = supabase.table('leave_requests').insert({
        'employee_id': employee_id,
        'company_id': company_id,
        'start_date': start_date,
        'end_date': end_date,
        'reason': reason,
        'status': 'Pending'
    }).execute()
    return response.data

def get_leave_requests_for_employee(employee_id):
    response = supabase.table('leave_requests').select('*').eq('employee_id', employee_id).order('created_at', desc=True).execute()
    return response.data

def get_leave_requests_for_company(company_id):
    # Supabase allows joining if foreign keys are set up. We'll fetch normally and manually map if join fails.
    # Let's try direct select first, if employee name mapping is needed, we'll do it manually.
    response = supabase.table('leave_requests').select('*').eq('company_id', company_id).order('created_at', desc=True).execute()
    
    # Manually fetch employee names to be safe
    if not response.data:
        return []
    
    leaves = response.data
    emp_ids = list(set([l['employee_id'] for l in leaves]))
    if emp_ids:
        emp_res = supabase.table('employees').select('employee_id, name').in_('employee_id', emp_ids).execute()
        emp_map = {e['employee_id']: e['name'] for e in emp_res.data}
        for l in leaves:
            l['employee_name'] = emp_map.get(l['employee_id'], 'Unknown')
            
    return leaves

def get_leave_balance(employee_id):
    # Rough approximation: assuming 20 leaves per year
    approved_leaves = supabase.table('leave_requests').select('start_date, end_date').eq('employee_id', employee_id).eq('status', 'Approved').execute()
    total_days_taken = 0
    from datetime import datetime
    for req in approved_leaves.data:
        s = datetime.strptime(req['start_date'], '%Y-%m-%d')
        e = datetime.strptime(req['end_date'], '%Y-%m-%d')
        total_days_taken += (e - s).days + 1
    return 20 - total_days_taken

# --- PHASE 4: OFFICE MANAGEMENT ---

def create_office(company_id, office_name, lat, lng, radius, timezone='UTC'):
    response = supabase.table('offices').insert({
        'company_id': company_id,
        'office_name': office_name,
        'latitude': lat,
        'longitude': lng,
        'radius': radius,
        'timezone': timezone
    }).execute()
    return response.data

def get_offices_for_company(company_id):
    response = supabase.table('offices').select('*').eq('company_id', company_id).execute()
    return response.data

def update_office(office_id, office_name, lat, lng, radius, timezone='UTC'):
    response = supabase.table('offices').update({
        'office_name': office_name,
        'latitude': lat,
        'longitude': lng,
        'radius': radius,
        'timezone': timezone
    }).eq('id', office_id).execute()
    return response.data

def delete_office(office_id):
    supabase.table('offices').delete().eq('id', office_id).execute()

def update_leave_status(leave_id, status):
    supabase.table('leave_requests').update({'status': status}).eq('id', leave_id).execute()

def update_attendance_status(log_id, is_present):
    supabase.table('attendance_logs').update({'is_present': is_present}).eq('id', log_id).execute()

def log_audit_action(action_type, user_id, user_role, details):
    supabase.table('audit_logs').insert({
        'action_type': action_type,
        'user_id': user_id,
        'user_role': user_role,
        'details': details
    }).execute()

def update_employee_rate(employee_id, new_rate):
    supabase.table('employees').update({'daily_rate': new_rate}).eq('employee_id', employee_id).execute()

def get_audit_logs_for_company(company_id):
    # Retrieve all logs related to this company or its employees
    # For prototype, we'll just pull all and filter or assume user_id is company_id for company actions
    response = supabase.table('audit_logs').select('*').order('created_at', desc=True).limit(100).execute()
    return response.data

def log_verification_event(employee_id, company_id, step_name, pass_fail, score, failure_reason=""):
    """
    Logs a verification event and routes to HR review queue if flagged.
    """
    import time
    for attempt in range(3):
        try:
            event_res = supabase.table('verification_events').insert({
                'employee_id': employee_id,
                'step_name': step_name,
                'pass_fail': pass_fail,
                'score': score,
                'failure_reason': failure_reason
            }).execute()
            
            if event_res.data and not pass_fail:
                failed_event_id = event_res.data[0]['id']
                supabase.table('attendance_overrides').insert({
                    'employee_id': employee_id,
                    'company_id': company_id,
                    'failed_event_id': failed_event_id,
                    'status': 'Pending'
                }).execute()
                
            return event_res.data
        except Exception as e:
            if attempt == 2:
                # Instead of crashing the whole login flow, just silently fail the log
                print(f"Non-critical DB Error: {e}")
                return None
            time.sleep(1)
