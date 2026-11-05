import httpx
import pytest
from fastapi import HTTPException

from elanco_client import ELANCO_URL, fetch_sightings


def test_fetch_sightings_cleans_successful_response(monkeypatch):
    sighting = {
        "id": "sighting-1",
        "date": "2022-08-01T06:40:31",
        "location": "Manchester",
        "species": "Marsh tick",
        "latinName": "Ixodes apronophorus",
    }

    def fake_get(url, timeout):
        assert url == ELANCO_URL
        assert timeout == 10.0

        return httpx.Response(
            200,
            json=[sighting, sighting, {"id": "incomplete"}],
            request=httpx.Request("GET", url),
        )

    monkeypatch.setattr("elanco_client.httpx.get", fake_get)

    result = fetch_sightings()

    assert result == [sighting]

@pytest.mark.parametrize(
    "error, expected_status",
    [
        (httpx.ReadTimeout("Simulated timeout"), 504),
        (httpx.ConnectError("Simulated connection failure"), 502),
    ],
)
def test_fetch_sightings_handles_connection_failures(
    monkeypatch, error, expected_status
):
    def fake_get(url, timeout):
        raise error

    monkeypatch.setattr("elanco_client.httpx.get", fake_get)

    with pytest.raises(HTTPException) as caught:
        fetch_sightings()

    assert caught.value.status_code == expected_status

@pytest.mark.parametrize("upstream_status", [429, 500, 503])
def test_fetch_sightings_handles_unsuccessful_statuses(
    monkeypatch, upstream_status
):
    def fake_get(url, timeout):
        return httpx.Response(
            upstream_status,
            json={"error": "Simulated upstream failure"},
            request=httpx.Request("GET", url),
        )

    monkeypatch.setattr("elanco_client.httpx.get", fake_get)

    with pytest.raises(HTTPException) as caught:
        fetch_sightings()

    assert caught.value.status_code == 502


@pytest.mark.parametrize(
    "body",
    [
        "this is not JSON",
        '{"message": "a dictionary instead of a list"}',
    ],
)
def test_fetch_sightings_rejects_invalid_response_data(monkeypatch, body):
    def fake_get(url, timeout):
        return httpx.Response(
            200,
            text=body,
            request=httpx.Request("GET", url),
        )

    monkeypatch.setattr("elanco_client.httpx.get", fake_get)

    with pytest.raises(HTTPException) as caught:
        fetch_sightings()

    assert caught.value.status_code == 502