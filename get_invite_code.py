import sys
sys.path.append('.')
from src.database.supabase_client import supabase

res = supabase.table('companys').select('name, company_invite_code').execute()
for c in res.data:
    print(f"Company: {c['name']}, Invite Code: {c['company_invite_code']}")
if not res.data:
    print("No companies found.")
