import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os

def load_data():

    try:
        db_url = st.secrets["DATABASE_URL"]
    except:
        db_url = os.getenv("SUPABASE_DB_URL")

    engine = create_engine(db_url)

    coop = pd.read_sql("SELECT * FROM cooperatives", engine)
    formation = pd.read_sql("SELECT * FROM formation", engine)
    coaching = pd.read_sql("SELECT * FROM coaching", engine)

    return coop, formation, coaching