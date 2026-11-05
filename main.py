from datetime import date, datetime

from processing import clean_sightings

import httpx
from fastapi import FastAPI, HTTPException

app = FastAPI(title="Elanco Tick Sightings API")

ELANCO_URL = "https://dev-task.elancoapps.com/data/tick-sightings"


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/sightings")
def get_sightings(
    location: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
):
    if start_date is not None and end_date is not None:
        if start_date > end_date:
            raise HTTPException(
                status_code=400,
                detail="start_date must be on or before end_date",
            )

    response = httpx.get(ELANCO_URL, timeout=10.0)
    response.raise_for_status()

    sightings = clean_sightings(response.json())
    filtered_sightings = []

    for sighting in sightings:
        sighting_date = datetime.fromisoformat(sighting["date"]).date()

        if location is not None:
            if sighting["location"].casefold() != location.strip().casefold():
                continue

        if start_date is not None and sighting_date < start_date:
            continue

        if end_date is not None and sighting_date > end_date:
            continue

        filtered_sightings.append(sighting)

    return filtered_sightings