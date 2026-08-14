import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Base EBP (source)
    EBP_SERVER: str = os.getenv("EBP_SERVER")
    EBP_DATABASE: str = os.getenv("EBP_DATABASE")
    EBP_USER: str = os.getenv("EBP_USER")
    EBP_PASSWORD: str = os.getenv("EBP_PASSWORD")
    
    # Base cible (BON DE PRODUCTION)
    SYNC_SERVER: str = os.getenv("SYNC_SERVER")
    SYNC_DATABASE: str = os.getenv("SYNC_DATABASE")
    SYNC_USER: str = os.getenv("SYNC_USER")
    SYNC_PASSWORD: str = os.getenv("SYNC_PASSWORD")
    
    # Driver ODBC
    ODBC_DRIVER: str = os.getenv("ODBC_DRIVER", "ODBC Driver 17 for SQL Server")
    
    # Synchro
    SYNC_INTERVAL_MINUTES: int = int(os.getenv("SYNC_INTERVAL_MINUTES", "5"))
    
settings = Settings()