from fastapi import APIRouter, HTTPException
from app.sync.service import sync_all_tables, sync_table_changes, initial_full_sync_all
from app.sync.tables import SYNC_TABLES

router = APIRouter()

last_sync_results = []


@router.post("/trigger")
def trigger_sync_all():
    """Déclenche une synchronisation manuelle incrémentale de toutes les tables."""
    global last_sync_results
    results = sync_all_tables()
    last_sync_results = results
    return {"message": "Synchronisation effectuée", "results": results}


@router.post("/{table_name}/trigger")
def trigger_sync_one(table_name: str):
    """Déclenche une synchronisation manuelle incrémentale d'une seule table."""
    if table_name not in SYNC_TABLES:
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' non gérée par la synchro")
    result = sync_table_changes(table_name)
    return {"message": f"Synchronisation de {table_name} effectuée", **result}


@router.post("/initial-load")
def trigger_initial_load():
    """Charge l'intégralité des données EBP pour toutes les tables (rejouable sans risque)."""
    results = initial_full_sync_all()
    return {"message": "Chargement initial effectué", "results": results}


@router.get("/status")
def sync_status():
    return {"last_sync": last_sync_results or "Aucune synchro effectuée pour l'instant"}