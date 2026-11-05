from processing import count_by_month


def test_count_by_month_groups_and_sorts_across_years():
    sightings = [
        {"date": "2023-01-15T12:00:00"},
        {"date": "2022-12-31T23:59:59"},
        {"date": "2022-01-10T09:00:00"},
        {"date": "2023-01-01T00:00:00"},
    ]

    result = count_by_month(sightings)

    assert result == {
        "2022-01": 1,
        "2022-12": 1,
        "2023-01": 2,
    }

    assert list(result.keys()) == [
        "2022-01",
        "2022-12",
        "2023-01",
    ]


def test_count_by_month_handles_empty_data():
    assert count_by_month([]) == {}