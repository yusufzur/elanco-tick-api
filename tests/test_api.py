import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

import main


client = TestClient(main.app)


@pytest.fixture
def sample_sightings(monkeypatch):
    sightings = [
        {
            "id": "1",
            "date": "2022-01-01T00:00:00",
            "location": "Manchester",
            "species": "Marsh tick",
            "latinName": "Ixodes apronophorus",
        },
        {
            "id": "2",
            "date": "2022-12-31T23:59:59",
            "location": "Manchester",
            "species": "Marsh tick",
            "latinName": "Ixodes apronophorus",
        },
        {
            "id": "3",
            "date": "2023-01-01T00:00:00",
            "location": "London",
            "species": "Marsh tick",
            "latinName": "Ixodes apronophorus",
        },
    ]

    def fake_fetch():
        return sightings

    monkeypatch.setattr(main, "fetch_sightings", fake_fetch)

    return sightings

def test_get_all_sightings(sample_sightings):
    response = client.get("/sightings")

    assert response.status_code == 200
    assert response.json() == sample_sightings


def test_combined_filters_include_both_boundary_dates(sample_sightings):
    response = client.get(
        "/sightings",
        params={
            "location": " manchester ",
            "start_date": "2022-01-01",
            "end_date": "2022-12-31",
        },
    )

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == ["1", "2"]


def test_unknown_location_returns_empty_list(sample_sightings):
    response = client.get(
        "/sightings",
        params={"location": "Atlantis"},
    )

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize(
    "params, expected_ids",
    [
        ({"start_date": "2023-01-01"}, ["3"]),
        ({"end_date": "2022-01-01"}, ["1"]),
    ],
)
def test_one_sided_date_filters(sample_sightings, params, expected_ids):
    response = client.get("/sightings", params=params)

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == expected_ids


@pytest.mark.parametrize(
    "params, expected_status",
    [
        (
            {"start_date": "2023-01-01", "end_date": "2022-01-01"},
            400,
        ),
        ({"start_date": "banana"}, 422),
    ],
)
def test_invalid_dates_do_not_fetch_data(monkeypatch, params, expected_status):
    def unexpected_fetch():
        pytest.fail("Invalid input should be rejected before fetching data")

    monkeypatch.setattr(main, "fetch_sightings", unexpected_fetch)

    response = client.get("/sightings", params=params)

    assert response.status_code == expected_status


def test_regional_stats(sample_sightings):
    response = client.get("/stats/regions")

    assert response.status_code == 200
    assert response.json() == {
        "North West": 2,
        "London": 1,
    }


def test_monthly_trends(sample_sightings):
    response = client.get("/stats/trends")

    assert response.status_code == 200
    assert response.json() == {
        "2022-01": 1,
        "2022-12": 1,
        "2023-01": 1,
    }


@pytest.mark.parametrize(
    "path",
    ["/sightings", "/stats/regions", "/stats/trends"],
)
def test_endpoints_return_fetch_errors_as_json(monkeypatch, path):
    def failing_fetch():
        raise HTTPException(
            status_code=504,
            detail="Simulated upstream timeout",
        )

    monkeypatch.setattr(main, "fetch_sightings", failing_fetch)

    response = client.get(path)

    assert response.status_code == 504
    assert response.json() == {
        "detail": "Simulated upstream timeout",
    }

def test_pagination_returns_requested_slice(sample_sightings):
    response = client.get(
        "/sightings",
        params={"limit": 1, "offset": 1},
    )

    assert response.status_code == 200
    assert response.json() == [sample_sightings[1]]


def test_pagination_happens_after_filtering(sample_sightings):
    response = client.get(
        "/sightings",
        params={"location": "London", "limit": 1, "offset": 0},
    )

    assert response.status_code == 200
    assert response.json() == [sample_sightings[2]]


def test_offset_beyond_results_returns_empty_list(sample_sightings):
    response = client.get(
        "/sightings",
        params={"offset": 100},
    )

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize(
    "params",
    [
        {"limit": 0},
        {"limit": 1001},
        {"offset": -1},
    ],
)
def test_invalid_pagination_is_rejected(sample_sightings, params):
    response = client.get("/sightings", params=params)

    assert response.status_code == 422