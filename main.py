from datetime import date, datetime

from fastapi import FastAPI, HTTPException

from elanco_client import fetch_sightings
from processing import count_by_region, count_by_month

app = FastAPI(title="Elanco Tick Sightings API")


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

    sightings = fetch_sightings()
    filtered_sightings = []

    for sighting in sightings:
        sighting_date = datetime.fromisoformat(sighting["date"]).date()

        if location is not None:
            if sighting["location"].strip().casefold() != location.strip().casefold():
                continue

        if start_date is not None and sighting_date < start_date:
            continue

        if end_date is not None and sighting_date > end_date:
            continue

        filtered_sightings.append(sighting)

    return filtered_sightings

@app.get("/stats/regions")
def get_regional_stats():
    sightings = fetch_sightings()
    return count_by_region(sightings)


@app.get("/stats/trends")
def get_monthly_trends():
    sightings = fetch_sightings()
    return count_by_month(sightings)