import sys
from datetime import datetime
sys.path.append('.')
from src.database.supabase_client import supabase

try:
    print("Finding company mahesh...")
    comp_res = supabase.table('companys').select('*').eq('company_invite_code', 'J3WWRN').execute()
    if not comp_res.data:
        print("Company not found!")
        sys.exit()
    company_id = comp_res.data[0]['id']
    
    print("Finding or creating a project...")
    sub_res = supabase.table('subjects').select('*').eq('company_id', company_id).execute()
    if not sub_res.data:
        res = supabase.table('subjects').insert({
            'subject_code': 'DEMO',
            'name': 'Demo Project',
            'section': 'A',
            'company_id': company_id
        }).execute()
        subject_id = res.data[0]['subject_id']
    else:
        subject_id = sub_res.data[0]['subject_id']
        
    print("Finding or creating an employee...")
    emp_res = supabase.table('employees').select('*').eq('company_id', company_id).execute()
    if not emp_res.data:
        res = supabase.table('employees').insert({
            'employee_code': 'EMP999',
            'name': 'Test Employee',
            'company_id': company_id
        }).execute()
        employee_id = res.data[0]['employee_id']
    else:
        employee_id = emp_res.data[0]['employee_id']
        
    print("Inserting attendance log...")
    supabase.table('attendance_logs').insert({
        'employee_id': employee_id,
        'subject_id': subject_id,
        'timestamp': datetime.now().isoformat(),
        'is_present': True,
        'latitude': 37.7749,
        'longitude': -122.4194,
        'location_status': 'Inside Office'
    }).execute()
    
    print("Success! Dummy record inserted.")

except Exception as e:
    print(f"Error: {str(e)}")
