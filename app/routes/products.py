from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text

from app.database.database import SyncSession

router = APIRouter()
class Color(BaseModel):
    CouleurId: str
    CodeCouleur: str
    CouleurCaption: str | None = None

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
    
@router.get("/couleurs/actives", response_model=List[Color])
def get_active_colors():
    query = text(" SELECT DISTINCT CouleurId, CodeCouleur, CouleurCaption FROM dbo.vw_OA_Actifs WHERE CodeCouleur IS NOT NULL ORDER BY CodeCouleur")
    try:
        with SyncSession() as db:
            results = db.execute(query).mappings().all()
            return results
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des codes couleurs")