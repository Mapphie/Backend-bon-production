from fastapi import APIRouter
from sqlalchemy import text

from app.database.database import SyncSession

router = APIRouter()

@router.get("/oa-actifs")
def get_oa_actifs():
    """Liste les articles des OA actifs (en attente ou traités partiellement)."""
    with SyncSession() as db:
        rows = db.execute(text("SELECT * FROM dbo.vw_OA_Actifs")).mappings().all()
        return [dict(r) for r in rows]