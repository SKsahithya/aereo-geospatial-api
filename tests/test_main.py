import geopandas as gpd
import pytest
from shapely.geometry import Point
from app.main import process_features
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert "running" in response.json()["message"]


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_upload_rejects_unsupported_file():
    response = client.post(
        "/api/files/",
        files={"file": ("test.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400
    assert "Only .kml and .zip files are supported." in response.json()["detail"]


def test_file_not_found():
    response = client.get("/api/files/invalid-test-id/")
    assert response.status_code == 404


def test_measurements_not_found():
    response = client.get(
        "/api/files/invalid-test-id/measurements/"
    )
    assert response.status_code == 404
def test_missing_crs_is_rejected():
    gdf = gpd.GeoDataFrame(
        {"name": ["test"]},
        geometry=[Point(78.4, 17.4)],
    )

    with pytest.raises(ValueError, match="no CRS"):
        process_features(gdf)