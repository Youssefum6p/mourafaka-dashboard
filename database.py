import os
import pandas as pd
from sqlalchemy import create_engine

# Use SUPABASE_DB_URL from environment
supabase_db_url = os.getenv("SUPABASE_DB_URL")
if not supabase_db_url:
    raise RuntimeError(
        "SUPABASE_DB_URL environment variable not set. "
        "Set it with:\n"
        "$env:SUPABASE_DB_URL='postgresql://postgres.ffyjufbxjqlhzmvnmswl:PASSWORD@aws-1-eu-central-1.pooler.supabase.com:5432/postgres?sslmode=require'"
    )

engine = create_engine(supabase_db_url)

def load_data():
    coop = pd.read_sql("SELECT * FROM cooperatives", engine)
    formation = pd.read_sql("SELECT * FROM formation", engine)
    coaching = pd.read_sql("SELECT * FROM coaching", engine)

    return coop, formation, coaching