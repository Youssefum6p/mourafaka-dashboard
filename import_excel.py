import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from urllib.parse import urlparse

# 1. Connexion Supabase
supabase_db_url = os.getenv("SUPABASE_DB_URL")
if supabase_db_url:
    if "YOUR_PASSWORD" in supabase_db_url or "your_password" in supabase_db_url:
        raise RuntimeError(
            "SUPABASE_DB_URL contains the placeholder YOUR_PASSWORD. "
            "Replace it with your actual password from Supabase."
        )

    parsed = urlparse(supabase_db_url)
    if parsed.scheme not in ("postgresql", "postgres"):
        raise RuntimeError("SUPABASE_DB_URL must start with postgresql://")
    if not parsed.username or not parsed.password:
        raise RuntimeError(
            "SUPABASE_DB_URL must include both username and password. "
            "Use the DIRECT_URL value from Supabase."
        )
    if parsed.username == "postgres":
        raise RuntimeError(
            "SUPABASE_DB_URL username appears to be plain 'postgres'. "
            "Use the full Supabase username from DIRECT_URL, for example: "
            "postgres.<project_ref>."
        )
    print(f"Using SUPABASE_DB_URL with user={parsed.username} host={parsed.hostname}")
    engine = create_engine(supabase_db_url)
else:
    SUPABASE_DB_USER = os.getenv("SUPABASE_DB_USER")
    SUPABASE_DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD")
    SUPABASE_DB_HOST = os.getenv("SUPABASE_DB_HOST")
    SUPABASE_DB_PORT = os.getenv("SUPABASE_DB_PORT")
    SUPABASE_DB_NAME = os.getenv("SUPABASE_DB_NAME")

    missing = [
        name for name, value in [
            ("SUPABASE_DB_USER", SUPABASE_DB_USER),
            ("SUPABASE_DB_PASSWORD", SUPABASE_DB_PASSWORD),
            ("SUPABASE_DB_HOST", SUPABASE_DB_HOST),
            ("SUPABASE_DB_PORT", SUPABASE_DB_PORT),
            ("SUPABASE_DB_NAME", SUPABASE_DB_NAME),
        ]
        if not value
    ]
    if missing:
        raise RuntimeError(
            "Set SUPABASE_DB_URL or all of SUPABASE_DB_USER, SUPABASE_DB_PASSWORD, "
            "SUPABASE_DB_HOST, SUPABASE_DB_PORT, SUPABASE_DB_NAME in your environment."
        )

    if "pooler.supabase.com" in SUPABASE_DB_HOST:
        raise RuntimeError(
            "The host appears to be a generic Supabase pooler endpoint. "
            "Use your project-specific Supabase DB host from the dashboard, "
            "for example: YOUR_PROJECT_REF.db.eu-central-1.supabase.co"
        )

    url = URL.create(
        drivername="postgresql+psycopg2",
        username=SUPABASE_DB_USER,
        password=SUPABASE_DB_PASSWORD,
        host=SUPABASE_DB_HOST,
        port=int(SUPABASE_DB_PORT),
        database=SUPABASE_DB_NAME,
        query={"sslmode": "require"},
    )
    engine = create_engine(url)

# 2. Lire les fichiers Excel
cooperatives = pd.read_excel("cooperatives.xlsx")
formation = pd.read_excel("formation.xlsx")
coaching = pd.read_excel("coaching.xlsx")

# 3. Envoyer vers Supabase
cooperatives.to_sql(
    "cooperatives",
    engine,
    if_exists="replace",
    index=False
)

formation.to_sql(
    "formation",
    engine,
    if_exists="replace",
    index=False
)

coaching.to_sql(
    "coaching",
    engine,
    if_exists="replace",
    index=False
)

print("Import terminé avec succès ✅")