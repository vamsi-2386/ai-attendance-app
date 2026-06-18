import os
# pyrefly: ignore [missing-import]
from supabase import create_client, Client
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_db_connection():
    # Deprecated for Supabase, but keeping it as a dummy or returning supabase client
    # Many places call conn = get_db_connection(), then conn.cursor(), conn.close()
    # This will break if we just return supabase here, so we must refactor db.py
    return supabase