# AEREO Geospatial File Measurement API

## Overview

The AEREO Geospatial File Measurement API is a REST API built using FastAPI and GeoPandas. It accepts geospatial files, extracts feature information, and calculates measurements for supported geometries.

## Features

- Upload KML files and ZIP archives containing a Shapefile.
- Extract feature geometry, properties, and coordinate reference system (CRS).
- Calculate polygon area in square metres.
- Calculate line length in metres.
- Retrieve uploaded file information.
- Retrieve measurements for all features.
- Handle unsupported files, invalid uploads, and missing file IDs.
- Provide a health-check endpoint.

## Technologies Used

- Python
- FastAPI
- Uvicorn
- GeoPandas
- Shapely
- PyProj
- Fiona
- Pytest
- HTTPX

## Project Structure

```text
aereo-geospatial-api/
├── app/
│   ├── __init__.py
│   └── main.py
├── tests/
│   └── test_main.py
├── uploads/
│   └── .gitkeep
├── sample.kml
├── requirements.txt
├── README.md
└── .gitignore
```

## Setup and Installation

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd aereo-geospatial-api
```

git clone https://github.com/SKsahithya/aereo-geospatial-api.git
cd aereo-geospatial-api

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment on Windows

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

## Run the Application

From the project root directory, run:

```bash
python -m uvicorn app.main:app --reload --port 8003
```

Open the interactive API documentation:

http://127.0.0.1:8003/docs

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Home endpoint |
| GET | `/health` | Check API health |
| POST | `/api/files/` | Upload a KML or ZIP Shapefile |
| GET | `/api/files/{file_id}/` | Retrieve file information |
| GET | `/api/files/{file_id}/measurements/` | Retrieve feature measurements |

## How to Use

1. Open `/docs` in your browser.
2. Expand `POST /api/files/`.
3. Click **Try it out** and select a `.kml` or `.zip` file.
4. Click **Execute** and copy the returned file ID.
5. Use the file ID with the file-information and measurements endpoints.

## Measurement Details

Each feature includes its feature ID, geometry type, geometry coordinates, CRS, and properties.

- Polygon and MultiPolygon geometries include `area_sq_m`.
- LineString and MultiLineString geometries include `length_m`.
- Unsupported measurement types return `null` for the relevant measurement.
- Files without a CRS are rejected because reliable measurements cannot be calculated without coordinate reference information.

Area and length are calculated using a projected coordinate reference system estimated from the input data.

## Error Handling

The API returns appropriate HTTP errors for unsupported file types, invalid ZIP archives, files without CRS information, processing failures, and unknown file IDs.

## Storage

Uploaded files are saved in the `uploads/` directory. Processed file information is stored in memory and is not retained after the application restarts.
## Architecture

The application is built using FastAPI and GeoPandas.

- **API layer:** FastAPI provides endpoints for file upload, file information, and feature measurements.
- **File-processing layer:** GeoPandas reads KML files and ZIP archives containing Shapefiles and extracts feature geometries, attributes, and CRS information.
- **Measurement layer:** Shapely and GeoPandas geometry operations are used to identify supported geometries and calculate measurements.
- **Storage:** Uploaded files are saved in the `uploads/` directory. Processed file metadata is maintained in memory.

### File-Processing Flow

1. The client uploads a KML or ZIP Shapefile.
2. The API validates the file extension and processes the file.
3. GeoPandas reads the geospatial data and extracts its features.
4. The application records feature information and the source CRS.
5. Supported geometries are measured using a suitable projected CRS.
6. The API returns file information or feature measurements as JSON.

### Measurement and CRS Handling

Geospatial measurements should not be calculated directly from longitude and latitude coordinates in EPSG:4326. The application estimates a suitable projected CRS and uses projected geometries for area and length calculations.

- Polygon and MultiPolygon: area in square metres.
- LineString and MultiLineString: length in metres.
- Point: no measurement is required.
- Unsupported geometry types: measurement fields are returned as `null` where applicable.

## Design Decisions

- **FastAPI:** Chosen for its lightweight API development, automatic OpenAPI documentation, and request validation.
- **GeoPandas:** Used to read geospatial formats and manage feature data and coordinate reference systems.
- **ZIP Shapefile uploads:** Shapefiles commonly consist of multiple related files, so the components are supplied together in a ZIP archive.
- **Projected CRS:** A projected coordinate system is used for measurement calculations instead of measuring geographic coordinates in degrees.
- **In-memory metadata:** A simple in-memory data structure keeps the initial implementation straightforward. It is suitable for a demonstration but does not persist file records across application restarts.

## Learning Outcomes

Through this project, I gained practical experience with:

- Building REST APIs using FastAPI.
- Reading KML and Shapefile data with GeoPandas.
- Working with geometries, feature attributes, and coordinate reference systems.
- Calculating geospatial area and length measurements.
- Handling invalid uploads and missing file IDs.
- Writing automated API tests with Pytest and TestClient.
- Documenting and managing a Python project with Git and GitHub.

## Future Scope

- Persist file metadata and processing results in a database.
- Add background processing for large geospatial files.
- Improve upload validation, file-size limits, and ZIP archive security.
- Add more comprehensive automated tests for points, multipart geometries, invalid CRS, and malformed files.
- Support additional geospatial formats such as GeoJSON.
- Improve CRS selection and add more measurement and validation options.

## Author

Developed as part of the AEREO Geospatial File Measurement API assignment.

## Run Tests

Run the automated tests from the project root directory:

```powershell
python -m pytest -v
```

The tests cover the home endpoint, health check, unsupported file uploads, and missing file IDs.