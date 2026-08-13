import os
import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

ODBC_DRIVER = os.getenv("ODBC_DRIVER", "ODBC Driver 17 for SQL Server")

def build_connectionn_url(server:str, database: str, user: str, password:str) -> str:
    """
        Contruit une URL de connexion SQLAlchemy/pyodbc pour SQL Server
    """
    
    params = urllib.parse.quote_plus(
        f"DRIVER={{{ODBC_DRIVER}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={user};"
        f"PWD={password};"
        f"TrustServerCertificate=yes;"
    )
    return f"mssql+pyodbc:///?odbc_connect={params}"


# --- Connexion à la base EBP (source, lecture seule)
EBP_URL = build_connectionn_url(
    server=os.getenv("EBP_SERVER"),
    database=os.getenv("EBP_DATABASE"),
    user=os.getenv("EBP_USER"),
    password=os.getenv("EBP_PASSWORD"),
)

ebp_engine = create_engine(EBP_URL, pool_pre_ping=True)
EbpSession = sessionmaker(bind=ebp_engine, autoflush=False, autocommit=False)

# Connexion à la base cible
PRODUCTION_DATABASE_URL = build_connectionn_url(
    server=os.getenv("PRODUCTION_SERVER"),
    database=os.getenv("PRODUCTION_DATABASE"),
    user=os.getenv("PRODUCTION_USER"),
    password=os.getenv("PRODUCTION_PASSWORD")
)

production_engine = create_engine(PRODUCTION_DATABASE_URL, pool_pre_ping=True)
ProductionSession = sessionmaker(bind=production_engine, autoflush=False, autocommit=False)

def get_ebp_db():
    session = EbpSession()
    try:
        yield session
    finally:
        session.close()
        
def get_sync_db():
    session = ProductionSession()
    try:
        yield session
    finally:session.close()