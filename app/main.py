
from fastapi import FastAPI, UploadFile, File, HTTPException
from pathlib import Path
from uuid import uuid4
from zipfile import ZipFile, BadZipFile
import tempfile
import math

import geopandas as gpd

app = FastAPI(
    title="AEREO Geospatial File Measurement API",
    description="Upload geospatial files and retrieve feature measurements.",
    version="1.0.0",
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Temporary in-memory storage for processed file information.
FILES = {}


def clean_value(value):
    """Convert non-JSON-compatible values to safe values."""
    if hasattr(value, "item"):
        value = value.item()

    if isinstance(value, float) and not math.isfinite(value):
        return None

    if isinstance(value, dict):
        return {str(k): clean_value(v) for k, v in value.items()}

    if isinstance(value, (list, tuple)):
        return [clean_value(v) for v in value]

    return value


@app.get("/")
def home():
    return {
        "message": "AEREO Geospatial File Measurement API is running"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


def read_geospatial_file(path: Path):
    """Read a KML file or a zipped Shapefile."""

    if path.suffix.lower() == ".kml":
        return gpd.read_file(path, driver="KML")

    if path.suffix.lower() == ".zip":
        with ZipFile(path) as archive:
            shapefiles = [
                name for name in archive.namelist()
                if name.lower().endswith(".shp")
                and not name.startswith("__MACOSX/")
            ]

            if len(shapefiles) != 1:
                raise ValueError(
                    "ZIP must contain exactly one Shapefile (.shp)."
                )

            with tempfile.TemporaryDirectory() as temp_dir:
                archive.extractall(temp_dir)
                shp_path = Path(temp_dir) / shapefiles[0]

                # Read the data before the temporary directory is removed.
                return gpd.read_file(shp_path).copy()

    raise ValueError("Only .kml and .zip files are supported.")


def process_features(gdf):
    """Extract feature details and calculate area and length."""

    if gdf.crs is None:
        raise ValueError(
            "The input file has no CRS. A reliable measurement "
            "cannot be calculated."
        )

    original_crs = str(gdf.crs)
    features = []

    # Project coordinates for measurement calculations.
    utm_crs = gdf.estimate_utm_crs()

    if utm_crs is None:
        raise ValueError("Could not determine a suitable projected CRS.")

    projected = gdf.to_crs(utm_crs)

    for index, (_, row) in enumerate(gdf.iterrows()):
        geometry = row.geometry
        projected_geometry = projected.geometry.iloc[index]

        area = None
        length = None

        geometry_type = (
            geometry.geom_type if geometry is not None else None
        )

        if geometry is not None and not geometry.is_empty:
            if geometry_type in ("Polygon", "MultiPolygon"):
                area = float(projected_geometry.area)

            elif geometry_type in ("LineString", "MultiLineString"):
                length = float(projected_geometry.length)

        properties = row.drop(labels=["geometry"]).to_dict()
        properties = clean_value(properties)

        feature = {
            "feature_id": index,
            "geometry_type": geometry_type,
            "geometry": (
                geometry.__geo_interface__
                if geometry is not None and not geometry.is_empty
                else None
            ),
            "crs": original_crs,
            "properties": properties,
            "area_sq_m": clean_value(area),
            "length_m": clean_value(length),
        }

        features.append(clean_value(feature))

    return features, original_crs


@app.post("/api/files/")
async def upload_file(file: UploadFile = File(...)):
    filename = file.filename or ""
    extension = Path(filename).suffix.lower()

    if extension not in (".kml", ".zip"):
        raise HTTPException(
            status_code=400,
            detail="Only .kml and .zip files are supported.",
        )

    file_id = str(uuid4())
    saved_path = UPLOAD_DIR / f"{file_id}{extension}"

    try:
        content = await file.read()

        if not content:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is empty.",
            )

        saved_path.write_bytes(content)

        try:
            gdf = read_geospatial_file(saved_path)
            features, crs = process_features(gdf)

        except (ValueError, BadZipFile) as exc:
            saved_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=400,
                detail=str(exc),
            ) from exc

        except Exception as exc:
            saved_path.unlink(missing_ok=True)
            raise HTTPException(
                status_code=400,
                detail=f"Could not process geospatial file: {exc}",
            ) from exc

        FILES[file_id] = {
            "id": file_id,
            "filename": filename,
            "feature_count": len(features),
            "crs": crs,
            "status": "COMPLETED",
            "features": features,
        }

        return {
            "id": file_id,
            "filename": filename,
            "feature_count": len(features),
            "crs": crs,
            "status": "COMPLETED",
        }

    finally:
        await file.close()


@app.get("/api/files/{file_id}/")
def get_file_info(file_id: str):
    if file_id not in FILES:
        raise HTTPException(
            status_code=404,
            detail="File not found.",
        )

    info = FILES[file_id]

    return {
        "id": info["id"],
        "filename": info["filename"],
        "feature_count": info["feature_count"],
        "crs": info["crs"],
        "status": info["status"],
    }


@app.get("/api/files/{file_id}/measurements/")
def get_measurements(file_id: str):
    if file_id not in FILES:
        raise HTTPException(
            status_code=404,
            detail="File not found.",
        )

    info = FILES[file_id]

    return {
        "id": file_id,
        "filename": info["filename"],
        "feature_count": info["feature_count"],
        "measurements": info["features"],
    }
