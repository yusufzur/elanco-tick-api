import httpx
from fastapi import FastAPI

app = FastAPI(title="Elanco Tick Sightings API")

ELANCO_URL = "https://dev-task.elancoapps.com/data/tick-sightings"


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/sightings")
def get_sightings():
    response = httpx.get(ELANCO_URL, timeout=10.0)
    response.raise_for_status()

    sightings = response.json()

    return sightings