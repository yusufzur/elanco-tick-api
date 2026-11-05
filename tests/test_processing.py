from processing import clean_sightings


def test_clean_sightings_removes_invalid_records_and_duplicate_ids():
    valid = {
        "id": "sighting-1",
        "date": "2022-08-01T06:40:31",
        "location": "Manchester",
        "species": "Marsh tick",
        "latinName": "Ixodes apronophorus",
    }

    invalid_first = {**valid, "location": ""}
    duplicate = {**valid, "location": "London"}
    invalid_date = {**valid, "id": "sighting-2", "date": "not-a-date"}
    missing_location = {
        key: value for key, value in valid.items() if key != "location"
    }
    separate_sighting = {**valid, "id": "sighting-3"}

    result = clean_sightings([
        invalid_first,
        valid,
        duplicate,
        invalid_date,
        missing_location,
        None,
        separate_sighting,
    ])

    assert result == [valid, separate_sighting]