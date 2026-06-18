import sys
from src.database.db import get_company_by_id, supabase
print(supabase.table('companys').select('*').execute().data)
