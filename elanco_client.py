import httpx
from fastapi import HTTPException

from processing import clean_sightings


ELANCO_URL = "https://dev-task.elancoapps.com/data/tick-sightings"


def fetch_sightings():
    try:
        response = httpx.get(ELANCO_URL, timeout=10.0)
        response.raise_for_status()
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Elanco's API took too long to respond. Please try again.",
        )
    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=502,
            detail="Elanco's API returned an unsuccessful response.",
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Unable to contact Elanco's API. Please try again.",
        )

    try:
        sightings = response.json()
    except ValueError:
        raise HTTPException(
            status_code=502,
            detail="Elanco's API returned invalid JSON.",
        )

    if not isinstance(sightings, list):
        raise HTTPException(
            status_code=502,
            detail="Elanco's API returned an unexpected data format.",
        )

    return clean_sightings(sightings)