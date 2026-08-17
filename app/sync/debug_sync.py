from app.database.database import sync_engine
from sqlalchemy import text

with sync_engine.connect() as conn:
    result = conn.execute(text("SELECT DB_NAME() AS current_db"))
    print("Connexion réussie à :", result.fetchone())