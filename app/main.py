from contextlib import asynccontextmanager
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
import logging

from app.core.config import settings
from app.sync.service import sync_all_tables
from app.routes import documents, sync, products

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sync")

scheduler = BackgroundScheduler()

def scheduled_sync():
    try:
        results = sync_all_tables()
        for r in results:
            if r["inserted_updated"] or r["deleted"]:
                logger.info(f"Sync {r['table']}: {r}")
    except Exception as e:
        logger.error(f"Erreur de synchro: {e}")
        
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Synchronisation initiale au démarrage...")
    try:
        results = sync_all_tables()
        for r in results:
            logger.info(f"Sync initiale {r['table']}: {r}")
    except Exception as e:
        logger.error(f"Erreur lors de la synchro initiale: {e}")

    scheduler.add_job(scheduled_sync, "interval", minutes=settings.SYNC_INTERVAL_MINUTES, id="sync_all")
    scheduler.start()

    yield

    scheduler.shutdown()
    
app = FastAPI(title="EBP Sync API", lifespan=lifespan)

app.include_router(sync.router, prefix="/sync", tags=["Synchronisation"])
app.include_router(products.router, tags=["Produits"])
app.include_router(documents.router, tags=["OA Actifs"])

@app.get("/")
def root():
    return {"status": "EBP Sync API en ligne"}