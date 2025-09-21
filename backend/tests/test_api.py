from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint.

    Tests that the root endpoint returns valid JSON with
    message and version information.
    """
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_check():
    """Test health check endpoint.

    Tests that the health check endpoint returns a successful
    status response.
    """
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_create_wsjf_item():
    """Test creating a WSJF item.

    Tests that a WSJF item can be created through the API
    and that the WSJF score is correctly calculated.
    """
    item_data = {
        "subject": "Test Feature",
        "description": "Test description",
        "business_value": 8,
        "time_criticality": 7,
        "risk_reduction": 6,
        "job_size": 5,
        "program_increment": "PI18",
    }

    response = client.post("/api/items", json=item_data)
    assert response.status_code == 201
    data = response.json()
    assert data["subject"] == "Test Feature"
    assert data["wsjf_score"] == 4.2  # (8+7+6)/5


def test_get_items():
    """Test getting all items.

    Tests that the API returns a list of WSJF items.
    """
    response = client.get("/api/items")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_sample_data():
    """Test generating sample data.

    Tests that the sample data endpoint creates demo WSJF items
    with proper priority rankings and WSJF scores.
    """
    response = client.get("/api/sample-data")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    # Check first item has priority
    first_item = data[0]
    assert "priority" in first_item
    assert "wsjf_score" in first_item
