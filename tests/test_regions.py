from processing import count_by_region


def test_count_by_region_groups_cities_and_keeps_unknown_locations():
    sightings = [
        {"location": "Manchester"},
        {"location": " liverpool "},
        {"location": "London"},
        {"location": "Unmapped City"},
    ]

    result = count_by_region(sightings)

    assert result == {
        "North West": 2,
        "London": 1,
        "Unknown": 1,
    }


def test_count_by_region_handles_empty_data():
    assert count_by_region([]) == {}