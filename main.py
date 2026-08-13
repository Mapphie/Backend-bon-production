from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from apscheduler.schedulers.background import BackgroundScheduler
from sync_service import sync_all_tables, SYNC_TABLES
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sync")

scheduler = BackgroundScheduler()
last_sync_results = []

def scheduled_sync():
    global last_sync_results
    try:
        results = sync_all_tables()
        last_sync_results = results
        for r in results:
            if r["inserted_updated"] or r["deleted"]:
                logger.info(f"Sync {r['table']}: {r}")
    except Exception as e:
        logger.error(f"Erreur de synchro: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Exécuté au démarrage ---
    logger.info("Synchronisation initiale au démarrage...")
    try:
        results = sync_all_tables()
        for r in results:
            logger.info(f"Sync initiale {r['table']}: {r}")
    except Exception as e:
        logger.error(f"Erreur lors de la synchro initiale: {e}")

    scheduler.add_job(scheduled_sync, "interval", minutes=5, id="sync_all")
    scheduler.start()

    yield  
    scheduler.shutdown()

app = FastAPI(title="EBP Sync API", lifespan=lifespan)

@app.get("/")
def root():
    return {"status": "EBP Sync API en ligne", "tables_suivies": list(SYNC_TABLES.keys())}
