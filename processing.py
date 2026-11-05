from datetime import datetime


def clean_sightings(sightings):
    cleaned = []
    seen_ids = set()

    required_fields = ["id", "date", "location", "species", "latinName"]

    for sighting in sightings:
        if not isinstance(sighting, dict):
            continue

        valid_fields = True

        for field in required_fields:
            value = sighting.get(field)

            if not isinstance(value, str) or not value.strip():
                valid_fields = False
                break

        if not valid_fields:
            continue

        try:
            datetime.fromisoformat(sighting["date"])
        except ValueError:
            continue

        sighting_id = sighting["id"]

        if sighting_id in seen_ids:
            continue

        seen_ids.add(sighting_id)
        cleaned.append(sighting)

    return cleaned


CITY_TO_REGION = {
    "manchester": "North West",
    "liverpool": "North West",
    "london": "London",
    "birmingham": "West Midlands",
    "southampton": "South East",
    "nottingham": "East Midlands",
    "leicester": "East Midlands",
    "sheffield": "Yorkshire and the Humber",
    "leeds": "Yorkshire and the Humber",
    "newcastle": "North East",
    "bristol": "South West",
    "glasgow": "Scotland",
    "edinburgh": "Scotland",
    "cardiff": "Wales",
}


def count_by_region(sightings):
    counts = {}

    for sighting in sightings:
        city = sighting["location"].strip().casefold()
        region = CITY_TO_REGION.get(city, "Unknown")

        if region not in counts:
            counts[region] = 0

        counts[region] += 1

    return counts

def count_by_month(sightings):
    counts = {}

    for sighting in sightings:
        sighting_date = datetime.fromisoformat(sighting["date"])
        month = sighting_date.strftime("%Y-%m")

        if month not in counts:
            counts[month] = 0

        counts[month] += 1

    return dict(sorted(counts.items()))