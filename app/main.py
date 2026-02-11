import json
import logging
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

logger = logging.getLogger("cpi-api")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

cpi_store = {
    "data": [],
    "by_iso2": {},
    "by_iso3": {},
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    data_path = Path(__file__).parent / "data" / "cpi_score.json"
    logger.info(f"Loading CPI data from {data_path}")
    with open(data_path, "r", encoding="utf-8") as f:
        cpi_store["data"] = json.load(f)
    cpi_store["by_iso2"] = {c["iso2"].upper(): c for c in cpi_store["data"]}
    cpi_store["by_iso3"] = {c["iso3"].upper(): c for c in cpi_store["data"]}
    logger.info(f"Loaded {len(cpi_store['data'])} countries")
    yield


app = FastAPI(
    title="CPI Score API",
    description="Corruption Perceptions Index — Public REST API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

from app.routes import router
app.include_router(router)