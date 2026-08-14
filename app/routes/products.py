from fastapi import APIRouter
from sqlalchemy import text

from app.database.database import SyncSession

router = APIRouter()

@router.get("/produits-gamme")
def get_produits_gamme():
    query = text("""
        SELECT Id, Caption, ItemType, xx_Article_bien
        FROM dbo.RangeItem
        ORDER BY Caption             
    """)
    with SyncSession() as db:
        rows = db.execute(query).mappings().all()
        return [dict(r) for r in rows]

@router.get("/couleurs")
def get_couleurs():
    query = text("""
        SELECT rte.Id as Id, rte.Code as CodeCouleur, it.Caption as CouleurCaption
        FROM dbo.RangeTypeElement rte
        LEFT JOIN dbo.Item it ON it.Id = rte.Code
        ORDER BY rte.Code             
    """)
    with SyncSession() as db:
        rows = db.execute(query).mappings().all()
        return [dict(r) for r in rows]