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