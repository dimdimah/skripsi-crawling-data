from dotenv import load_dotenv
import os
from supabase import create_client

load_dotenv()

def get_supabase():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")

    if not url or not key:
        raise ValueError("Missing Supabase env")

    return create_client(url, key)

supabase = get_supabase()