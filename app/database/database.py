from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import urllib.parse
from app.core.config import settings


def build_connection_url(server: str, database: str, user: str, password: str) -> str:
    params = urllib.parse.quote_plus(
        f"DRIVER={{{settings.ODBC_DRIVER}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={user};"
        f"PWD={password};"
        f"TrustServerCertificate=yes;"
    )
    return f"mssql+pyodbc:///?odbc_connect={params}"


EBP_URL = build_connection_url(
    settings.EBP_SERVER, settings.EBP_DATABASE, settings.EBP_USER, settings.EBP_PASSWORD
)
ebp_engine = create_engine(EBP_URL, pool_pre_ping=True)
EbpSession = sessionmaker(bind=ebp_engine, autoflush=False, autocommit=False)

SYNC_URL = build_connection_url(
    settings.SYNC_SERVER, settings.SYNC_DATABASE, settings.SYNC_USER, settings.SYNC_PASSWORD
)
sync_engine = create_engine(SYNC_URL, pool_pre_ping=True)
SyncSession = sessionmaker(bind=sync_engine, autoflush=False, autocommit=False)

def get_ebp_db():
    db = EbpSession()
    try:
        yield db
    finally:
        db.close()


def get_sync_db():
    db = SyncSession()
    try:
        yield db
    finally:
        db.close()