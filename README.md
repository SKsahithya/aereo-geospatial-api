# AEREO Geospatial File Measurement API

## Overview

The AEREO Geospatial File Measurement API is a REST API built using FastAPI and GeoPandas. It accepts geospatial files, extracts feature information, and calculates measurements for supported geometries.

The application supports KML files and ZIP archives containing Shapefiles. It returns feature geometry, properties, coordinate reference system (CRS), and measurement results through REST API endpoints.

## Features

- Upload KML files and ZIP archives containing Shapefiles.
- Extract feature IDs, geometry types, geometries, properties, and CRS information.
- Calculate polygon area in square metres.
- Calculate line length in metres.
- Transform geographic coordinates to a suitable projected CRS before measuring.
- Retrieve uploaded file information.
- Retrieve measurements for all features in an uploaded file.
- Handle unsupported file types, invalid uploads, and missing file IDs.
- Provide home and health-check endpoints.
- Include automated tests using Pytest.

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
git clone https://github.com/SKsahithya/aereo-geospatial-api.git
cd aereo-geospatial-api
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell prevents activation, you can use Command Prompt instead:

```cmd
.venv\Scripts\activate.bat
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

## Run the Application

From the project root directory, start the FastAPI server:

```bash
python -m uvicorn app.main:app --reload --port 8003
```

Open the interactive API documentation in your browser:

http://127.0.0.1:8003/docs

The application also provides a health-check endpoint at:

http://127.0.0.1:8003/health

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Returns a home message |
| GET | `/health` | Checks API health |
| POST | `/api/files/` | Uploads and processes a KML or ZIP Shapefile |
| GET | `/api/files/{file_id}/` | Retrieves uploaded file information |
| GET | `/api/files/{file_id}/measurements/` | Retrieves measurements for the uploaded features |

### 1. Upload a Geospatial File

**Endpoint:** `POST /api/files/`

This endpoint accepts a `.kml` file or a `.zip` archive containing a Shapefile.

**Example request using cURL:**

```bash
curl -X POST "http://127.0.0.1:8003/api/files/" -F "file=@sample.kml"
```

**Example response:**

```json
{
  "id": "abc123",
  "filename": "sample.kml",
  "feature_count": 2,
  "crs": "EPSG:4326",
  "status": "COMPLETED"
}
```

The returned file ID can be used to retrieve file information and feature measurements.

### 2. Retrieve File Information

**Endpoint:** `GET /api/files/{file_id}/`

**Example request:**

```bash
curl "http://127.0.0.1:8003/api/files/abc123/"
```

**Example response:**

```json
{
  "id": "abc123",
  "filename": "sample.kml",
  "feature_count": 2,
  "crs": "EPSG:4326",
  "status": "COMPLETED"
}
```

### 3. Retrieve Feature Measurements

**Endpoint:** `GET /api/files/{file_id}/measurements/`

**Example request:**

```bash
curl "http://127.0.0.1:8003/api/files/abc123/measurements/"
```

**Example response structure:**

```json
{
  "id": "abc123",
  "filename": "sample.kml",
  "feature_count": 2,
  "measurements": [
    {
      "feature_id": 0,
      "geometry_type": "Polygon",
      "geometry": {
        "type": "Polygon",
        "coordinates": []
      },
      "crs": "EPSG:4326",
      "properties": {},
      "area_sq_m": 1180462.65,
      "length_m": null
    }
  ]
}
```

**Note:** The examples are illustrative. The file ID, feature count, feature properties, geometry coordinates, and measurement values depend on the uploaded file. Replace `abc123` with the actual ID returned by the upload endpoint.

## How to Use the API

1. Start the application using the command provided above.
2. Open `http://127.0.0.1:8003/docs`.
3. Expand `POST /api/files/`.
4. Click **Try it out** and select a `.kml` file or `.zip` Shapefile.
5. Click **Execute** and note the returned file ID.
6. Use that ID with `GET /api/files/{file_id}/` to retrieve file information.
7. Use that ID with `GET /api/files/{file_id}/measurements/` to retrieve feature measurements.

## Measurement Details

For every feature, the API provides its feature ID, geometry type, geometry coordinates, CRS, and properties.

The supported measurement behaviour is:

- **Polygon and MultiPolygon:** Calculate area in square metres.
- **LineString and MultiLineString:** Calculate length in metres.
- **Point:** No measurement is required.
- **Other geometry types:** Return no area or length measurement where applicable.

Measurements are calculated using projected geometries rather than directly using longitude and latitude coordinates.

The application estimates a suitable projected CRS from the input dataset and transforms the geometries before calculating area and length.

Files without CRS information are rejected because a reliable measurement cannot be calculated without knowing the coordinate reference system.

## Error Handling

The API handles common upload and processing errors, including:

- Unsupported file extensions.
- Empty uploaded files.
- Invalid ZIP archives.
- ZIP archives without exactly one usable Shapefile.
- Files without CRS information.
- Geospatial processing failures.
- Requests for unknown file IDs.

Appropriate HTTP error responses are returned when these situations occur.

## Storage

Uploaded files are saved in the `uploads/` directory.

Processed file information and measurement results are stored in an in-memory data structure. Consequently, file records are not retained after the application restarts.

This storage approach keeps the initial implementation simple. Persistent database storage can be introduced in a future version.

## Architecture

The application is organized into the following logical layers:

- **API layer:** FastAPI exposes endpoints for file upload, file information, health checks, and feature measurements.
- **File-processing layer:** GeoPandas reads KML files and ZIP archives containing Shapefiles and extracts feature geometries, attributes, and CRS information.
- **Measurement layer:** GeoPandas and Shapely geometry operations identify supported geometries and calculate area and length.
- **Storage layer:** Uploaded files are saved on disk, while processed metadata and measurements are held in memory.

### File-Processing Flow

1. The client uploads a KML file or ZIP Shapefile.
2. The API validates the file extension and checks that the upload is not empty.
3. GeoPandas reads the geospatial data.
4. The application extracts feature geometries, attributes, geometry types, and source CRS.
5. The application estimates a suitable projected CRS and transforms geometries for measurement.
6. The application calculates supported measurements and stores the processed results.
7. The API returns file information or feature measurements as JSON.

### Measurement and CRS Handling

Geographic coordinate systems such as EPSG:4326 represent positions using longitude and latitude. These coordinates are expressed in degrees, so they should not be used directly for planar area or length calculations.

The application estimates a suitable projected CRS from the input dataset and transforms the geometries using GeoPandas before calculating measurements.

- Polygon and MultiPolygon geometries are measured for area in square metres.
- LineString and MultiLineString geometries are measured for length in metres.
- Point geometries do not require measurements.
- Unsupported geometry types are handled without requiring area or length calculations.

The estimated CRS approach is intended for suitable datasets, particularly geographically local data. Very large or geographically dispersed datasets may require a more specialized CRS selection strategy.

## Design Decisions

### FastAPI

FastAPI was chosen because it supports lightweight REST API development, request validation, and automatically generated interactive API documentation.

Django REST Framework was another permitted option, but FastAPI was suitable for this focused API.

### GeoPandas

GeoPandas was selected to read geospatial data, work with feature attributes and geometries, and transform coordinate reference systems.

### ZIP Archives for Shapefiles

A Shapefile commonly consists of multiple related files. Accepting a ZIP archive allows these files to be uploaded together.

The application checks the archive for a usable Shapefile before processing it.

### Projected CRS for Measurements

Area and length are calculated after transforming geometries into an estimated projected CRS. This avoids incorrectly calculating planar measurements directly from longitude and latitude coordinates.

### In-Memory Metadata

An in-memory data structure was chosen to keep the initial implementation simple and easy to understand. A database would be more suitable for persistent records and a larger deployment.

## Learning Outcomes

Through this project, I gained practical experience with:

- Building REST APIs using FastAPI.
- Reading KML and Shapefile data using GeoPandas.
- Working with geometries, feature attributes, and coordinate reference systems.
- Calculating geospatial area and length measurements.
- Handling invalid uploads and missing file IDs.
- Writing automated tests using Pytest and FastAPI TestClient.
- Organizing a Python project and managing source code with Git and GitHub.

## Future Scope

Potential improvements include:

- Persisting file metadata and measurement results in a database.
- Adding background processing for large geospatial files.
- Enforcing upload size limits and improving ZIP archive security.
- Expanding automated tests for additional geometry types and invalid inputs.
- Supporting additional geospatial formats such as GeoJSON.
- Improving CRS selection for large or geographically dispersed datasets.
- Adding more robust validation and production monitoring.

## Run Tests

Run the automated tests from the project root directory:

```bash
python -m pytest -v
```

The current tests cover the home endpoint, health check, unsupported file uploads, and missing file IDs. Update this description if additional tests are added.

## Author

Developed as part of the AEREO Geospatial File Measurement API assignment.
