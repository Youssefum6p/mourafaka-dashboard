import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

def load_data():

    # connexion Supabase depuis Streamlit Secrets
    db_url = st.secrets["DATABASE_URL"]

    engine = create_engine(db_url)

    coop = pd.read_sql("SELECT * FROM cooperatives", engine)
    formation = pd.read_sql("SELECT * FROM formation", engine)
    coaching = pd.read_sql("SELECT * FROM coaching", engine)

    return coop, formation, coaching