# Elanco Tick Sightings API

A Python and FastAPI backend built for the Elanco Software Engineer Placement task.

The application retrieves tick sightings from Elanco’s API, removes invalid and duplicate records, supports location and date filtering, and provides regional statistics and monthly trends.

**Author:** YUSUF ZIYA URHAN

## Run the project

Clone the repository:

```bash
git clone https://github.com/yusufzur/elanco-tick-api.git
cd elanco-tick-api
```

Create and activate a virtual environment on macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

Install dependencies and start the development server:

```bash
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Open the [interactive API documentation](http://127.0.0.1:8000/docs) to try the endpoints.

The data endpoints require an internet connection. No Elanco API key is needed.

## Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Check that this application is running |
| GET | `/sightings` | Return cleaned sightings with optional filtering and pagination |
| GET | `/stats/regions` | Count all cleaned sightings by region |
| GET | `/stats/trends` | Count all cleaned sightings by calendar month |

`/health` does not check the availability of Elanco’s API. The statistics endpoints use all cleaned sightings and do not accept filters.

### Filtering and pagination

`/sightings` accepts these optional query parameters:

| Parameter | Default | Behaviour |
|---|---|---|
| `location` | Unset | Exact city match, ignoring case and surrounding spaces |
| `start_date` | Unset | Include sightings on or after this date |
| `end_date` | Unset | Include sightings on or before this date |
| `limit` | `100` | Number of records to return, from 1 to 1000 |
| `offset` | `0` | Number of matching records to skip |

Dates use `YYYY-MM-DD`. Both boundaries are inclusive, and either date can be supplied independently. Pagination is applied after filtering.

Example: Manchester sightings during 2022:

```bash
curl "http://127.0.0.1:8000/sightings?location=Manchester&start_date=2022-01-01&end_date=2022-12-31&limit=20&offset=0"
```

Example: regional counts and monthly trends:

```bash
curl "http://127.0.0.1:8000/stats/regions"
curl "http://127.0.0.1:8000/stats/trends"
```

A valid search with no matches returns an empty list and HTTP 200.

## Architecture and technology choices

```text
main.py              Endpoints, request validation, filtering and pagination
elanco_client.py     External API requests and failure handling
processing.py        Data cleaning and aggregation
tests/               Processing, external API and endpoint tests
requirements.txt     Python dependencies
```

- **Python** keeps the processing logic readable using lists, dictionaries and sets.
- **FastAPI** provides request validation and interactive API documentation.
- **HTTPX** handles requests to Elanco.
- **pytest** supports repeatable tests with controlled data.

Each data request fetches the source records, validates the response, cleans the data, and then filters or aggregates it.

The MVP processes data in memory without a database. This keeps setup simple, but limits scalability.

## Data handling decisions

### Invalid and incomplete records

Records must contain non-empty strings for `id`, `date`, `location`, `species` and `latinName`. Dates must be parseable.

Invalid records are skipped so they do not break filtering or reporting. This strict policy also excludes otherwise useful records with missing species information.

### Duplicate handling

The first valid record for each ID is retained. A set tracks accepted IDs, allowing efficient duplicate checks.

Later records with the same ID are discarded, including conflicting records. Different IDs are retained even when their other fields match, as they may represent separate sightings.

### Regional statistics

Elanco supplies cities rather than regions. An explicit mapping groups English cities into English regions, with Scottish and Welsh cities grouped under Scotland and Wales.

This is a reporting convention rather than a uniform administrative geography. Unmapped cities are counted under `Unknown`.

### Monthly trends

Sightings are grouped by year and month using `YYYY-MM` and returned in chronological order. Months with no sightings are omitted.

Dates are interpreted as supplied, without timezone conversion. Counts describe reporting activity and should not be interpreted as disease-risk estimates.

## Error handling

| Status | Meaning |
|---|---|
| `400` | Start date is later than end date |
| `422` | Invalid request parameters |
| `502` | Upstream request failure, unsuccessful status, invalid JSON or unexpected response structure |
| `504` | Upstream request timeout |

HTTPX uses a 10-second timeout for network operations. Errors return a JSON `detail` message rather than misleading callers with an empty list.

Upstream rate-limit responses currently become HTTP 502. Automatic retries are not implemented.

## Testing

Run the tests with the virtual environment activated:

```bash
python -m pytest
```

Tests cover cleaning, duplicate handling, regional counts, monthly trends, filtering, pagination, invalid inputs and error responses.

External requests are replaced with controlled responses, so tests do not depend on Elanco’s availability. Endpoint tests use FastAPI’s test client without requiring a running server.

## Limitations and future improvements

- Each data request downloads and processes the full upstream dataset. Pagination reduces the response size, not the upstream workload.
- Larger datasets would benefit from scheduled ingestion, database indexes and upstream pagination if supported.
- A short-lived cache could reduce repeated requests, with an explicit refresh and failure policy.
- Invalid and duplicate records are skipped without reporting removal counts. Logging and data-quality metrics would improve visibility.
- The city-to-region mapping requires manual maintenance.
- Sightings preserve upstream order, so changes to the dataset can shift page contents between requests.
- Paginated responses do not include total counts or next-page links.
- Authentication, persistent storage and AI/ML insights are outside this MVP.

The implementation prioritises the core requirements and testable behaviour. An optional future extension could investigate unusual monthly reporting patterns, with careful evaluation of data quality and seasonal effects.

## Data source

[Elanco API documentation](https://dev-task.elancoapps.com)

The application retrieves data from `/data/tick-sightings`. The source is provided for the placement exercise and educational use.