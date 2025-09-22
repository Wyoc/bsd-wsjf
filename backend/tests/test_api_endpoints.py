"""Tests for API endpoints."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def api_client_with_db(clean_database):
    """Create API client with clean test database."""
    # Patch the database manager in the services
    with (
        patch("app.services.wsjf_service.wsjf_service.db", clean_database),
        patch("app.services.pi_service.pi_service.db", clean_database),
    ):
        yield TestClient(app)


class TestHealthEndpoints:
    """Test health and basic endpoints."""

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert data["message"] == "WSJF Excel Generator API"
        assert "version" in data
        assert "docs" in data

    def test_health_endpoint(self, api_client_with_db):
        """Test health check endpoint."""
        response = api_client_with_db.get("/api/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "WSJF API"


class TestProgramIncrementEndpoints:
    """Test Program Increment API endpoints."""

    @pytest.fixture
    def sample_pi_data(self):
        """Sample PI data for testing."""
        return {
            "name": "PI20",
            "description": "Test Program Increment 20",
            "start_date": "2025-01-01T00:00:00Z",
            "end_date": "2025-03-31T23:59:59Z",
            "status": "Planning",
        }

    def test_get_all_pis_empty(self, api_client_with_db):
        """Test getting all PIs when none exist."""
        response = api_client_with_db.get("/api/pis/")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_pi(self, api_client_with_db, sample_pi_data):
        """Test creating a new Program Increment."""
        response = api_client_with_db.post("/api/pis/", json=sample_pi_data)
        assert response.status_code == 201

        data = response.json()
        assert data["name"] == sample_pi_data["name"]
        assert data["description"] == sample_pi_data["description"]
        assert data["status"] == sample_pi_data["status"]
        assert "id" in data
        assert "created_date" in data

    def test_create_pi_duplicate_name(self, api_client_with_db, sample_pi_data):
        """Test creating PI with duplicate name fails."""
        # Create first PI
        response1 = api_client_with_db.post("/api/pis/", json=sample_pi_data)
        assert response1.status_code == 201

        # Try to create second PI with same name
        response2 = api_client_with_db.post("/api/pis/", json=sample_pi_data)
        assert response2.status_code == 500  # Database constraint violation

    def test_create_pi_invalid_data(self, api_client_with_db):
        """Test creating PI with invalid data."""
        invalid_data = {
            "name": "",  # Empty name
            "start_date": "invalid-date",
            "end_date": "2025-03-31T23:59:59Z",
        }

        response = api_client_with_db.post("/api/pis/", json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_get_all_pis(self, api_client_with_db, sample_pi_data):
        """Test getting all PIs."""
        # Create a PI first
        create_response = api_client_with_db.post("/api/pis/", json=sample_pi_data)
        assert create_response.status_code == 201

        # Get all PIs
        response = api_client_with_db.get("/api/pis/")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == sample_pi_data["name"]
        assert data[0]["item_count"] == 0

    def test_get_pi_by_id(self, api_client_with_db, sample_pi_data):
        """Test getting PI by ID."""
        # Create a PI first
        create_response = api_client_with_db.post("/api/pis/", json=sample_pi_data)
        pi_id = create_response.json()["id"]

        # Get PI by ID
        response = api_client_with_db.get(f"/api/pis/{pi_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == pi_id
        assert data["name"] == sample_pi_data["name"]

    def test_get_pi_by_id_not_found(self, api_client_with_db):
        """Test getting non-existent PI by ID."""
        from uuid import uuid4

        non_existent_id = str(uuid4())

        response = api_client_with_db.get(f"/api/pis/{non_existent_id}")
        assert response.status_code == 404

    def test_get_pi_by_name(self, api_client_with_db, sample_pi_data):
        """Test getting PI by name."""
        # Create a PI first
        create_response = api_client_with_db.post("/api/pis/", json=sample_pi_data)
        assert create_response.status_code == 201

        # Get PI by name
        response = api_client_with_db.get(f"/api/pis/name/{sample_pi_data['name']}")
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == sample_pi_data["name"]

    def test_get_pi_by_name_not_found(self, api_client_with_db):
        """Test getting non-existent PI by name."""
        response = api_client_with_db.get("/api/pis/name/NonExistentPI")
        assert response.status_code == 404

    def test_update_pi(self, api_client_with_db, sample_pi_data):
        """Test updating a Program Increment."""
        # Create a PI first
        create_response = api_client_with_db.post("/api/pis/", json=sample_pi_data)
        pi_id = create_response.json()["id"]

        # Update PI
        update_data = {
            "name": "Updated PI20",
            "description": "Updated description",
            "status": "Active",
        }

        response = api_client_with_db.put(f"/api/pis/{pi_id}", json=update_data)
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == "Updated PI20"
        assert data["description"] == "Updated description"
        assert data["status"] == "Active"

    def test_update_pi_not_found(self, api_client_with_db):
        """Test updating non-existent PI."""
        from uuid import uuid4

        non_existent_id = str(uuid4())

        update_data = {"name": "Updated Name"}
        response = api_client_with_db.put(
            f"/api/pis/{non_existent_id}", json=update_data
        )
        assert response.status_code == 404

    def test_delete_pi(self, api_client_with_db, sample_pi_data):
        """Test deleting a Program Increment."""
        # Create a PI first
        create_response = api_client_with_db.post("/api/pis/", json=sample_pi_data)
        pi_id = create_response.json()["id"]

        # Delete PI
        response = api_client_with_db.delete(f"/api/pis/{pi_id}")
        assert response.status_code == 204

        # Verify PI is deleted
        get_response = api_client_with_db.get(f"/api/pis/{pi_id}")
        assert get_response.status_code == 404

    def test_delete_pi_not_found(self, api_client_with_db):
        """Test deleting non-existent PI."""
        from uuid import uuid4

        non_existent_id = str(uuid4())

        response = api_client_with_db.delete(f"/api/pis/{non_existent_id}")
        assert response.status_code == 404

    def test_get_pi_stats(self, api_client_with_db, sample_pi_data):
        """Test getting PI statistics."""
        # Create a PI first
        create_response = api_client_with_db.post("/api/pis/", json=sample_pi_data)
        pi_id = create_response.json()["id"]

        # Get PI stats
        response = api_client_with_db.get(f"/api/pis/{pi_id}/stats")
        assert response.status_code == 200

        data = response.json()
        assert data["pi_id"] == pi_id
        assert data["pi_name"] == sample_pi_data["name"]
        assert data["total_items"] == 0
        assert data["avg_wsjf_score"] == 0.0
        assert data["status_distribution"] == {}
        assert data["team_distribution"] == {}


class TestWSJFItemEndpoints:
    """Test WSJF Item API endpoints."""

    @pytest.fixture
    def sample_pi(self, api_client_with_db):
        """Create a sample PI for testing WSJF items."""
        pi_data = {
            "name": "Test PI for Items",
            "description": "PI for testing WSJF items",
            "start_date": "2025-01-01T00:00:00Z",
            "end_date": "2025-03-31T23:59:59Z",
            "status": "Planning",
        }

        response = api_client_with_db.post("/api/pis/", json=pi_data)
        assert response.status_code == 201
        return response.json()

    @pytest.fixture
    def sample_wsjf_item_data(self, sample_pi):
        """Sample WSJF item data for testing."""
        return {
            "subject": "Test Authentication System",
            "description": "Implement secure login system",
            "business_value": {
                "pms_business": 21,
                "dev_technical": 13,
                "ia_business": 8,
            },
            "time_criticality": {"consultants_business": 13, "support_business": 5},
            "risk_reduction": {"dev_business": 8, "devops_technical": 3},
            "job_size": {"dev": 5, "ia": 3, "devops": 2, "exploit": 1},
            "owner": "Test Owner",
            "team": "Test Team",
            "program_increment_id": sample_pi["id"],
        }

    def test_get_all_items_empty(self, api_client_with_db):
        """Test getting all WSJF items when none exist."""
        response = api_client_with_db.get("/api/items")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_item(self, api_client_with_db, sample_wsjf_item_data):
        """Test creating a new WSJF item."""
        response = api_client_with_db.post("/api/items", json=sample_wsjf_item_data)
        assert response.status_code == 201

        data = response.json()
        assert data["subject"] == sample_wsjf_item_data["subject"]
        assert data["description"] == sample_wsjf_item_data["description"]
        assert data["owner"] == sample_wsjf_item_data["owner"]
        assert data["team"] == sample_wsjf_item_data["team"]
        assert "id" in data
        assert "created_date" in data
        assert "wsjf_score" in data
        assert data["wsjf_score"] > 0

    def test_create_item_invalid_data(self, api_client_with_db):
        """Test creating WSJF item with invalid data."""
        invalid_data = {
            "subject": "",  # Empty subject
            "business_value": {},  # Empty business value
        }

        response = api_client_with_db.post("/api/items", json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_get_all_items(self, api_client_with_db, sample_wsjf_item_data):
        """Test getting all WSJF items."""
        # Create an item first
        create_response = api_client_with_db.post(
            "/api/items", json=sample_wsjf_item_data
        )
        assert create_response.status_code == 201

        # Get all items
        response = api_client_with_db.get("/api/items")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 1
        assert data[0]["subject"] == sample_wsjf_item_data["subject"]
        assert data[0]["priority"] == 1

    def test_get_items_by_program_increment(
        self, api_client_with_db, sample_wsjf_item_data, sample_pi
    ):
        """Test filtering items by program increment."""
        # Create an item
        create_response = api_client_with_db.post(
            "/api/items", json=sample_wsjf_item_data
        )
        assert create_response.status_code == 201

        # Get items filtered by PI
        response = api_client_with_db.get(
            f"/api/items?program_increment_id={sample_pi['id']}"
        )
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 1
        assert data[0]["program_increment_id"] == sample_pi["id"]

    def test_get_item_by_id(self, api_client_with_db, sample_wsjf_item_data):
        """Test getting WSJF item by ID."""
        # Create an item first
        create_response = api_client_with_db.post(
            "/api/items", json=sample_wsjf_item_data
        )
        item_id = create_response.json()["id"]

        # Get item by ID
        response = api_client_with_db.get(f"/api/items/{item_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == item_id
        assert data["subject"] == sample_wsjf_item_data["subject"]

    def test_get_item_by_id_not_found(self, api_client_with_db):
        """Test getting non-existent WSJF item by ID."""
        from uuid import uuid4

        non_existent_id = str(uuid4())

        response = api_client_with_db.get(f"/api/items/{non_existent_id}")
        assert response.status_code == 404

    def test_update_item(self, api_client_with_db, sample_wsjf_item_data):
        """Test updating a WSJF item."""
        # Create an item first
        create_response = api_client_with_db.post(
            "/api/items", json=sample_wsjf_item_data
        )
        item_id = create_response.json()["id"]

        # Update item
        update_data = {
            "subject": "Updated Authentication System",
            "description": "Updated description",
            "status": "Go",
        }

        response = api_client_with_db.put(f"/api/items/{item_id}", json=update_data)
        assert response.status_code == 200

        data = response.json()
        assert data["subject"] == "Updated Authentication System"
        assert data["description"] == "Updated description"
        assert data["status"] == "Go"

    def test_update_item_not_found(self, api_client_with_db):
        """Test updating non-existent WSJF item."""
        from uuid import uuid4

        non_existent_id = str(uuid4())

        update_data = {"subject": "Updated Subject"}
        response = api_client_with_db.put(
            f"/api/items/{non_existent_id}", json=update_data
        )
        assert response.status_code == 404

    def test_delete_item(self, api_client_with_db, sample_wsjf_item_data):
        """Test deleting a WSJF item."""
        # Create an item first
        create_response = api_client_with_db.post(
            "/api/items", json=sample_wsjf_item_data
        )
        item_id = create_response.json()["id"]

        # Delete item
        response = api_client_with_db.delete(f"/api/items/{item_id}")
        assert response.status_code == 204

        # Verify item is deleted
        get_response = api_client_with_db.get(f"/api/items/{item_id}")
        assert get_response.status_code == 404

    def test_delete_item_not_found(self, api_client_with_db):
        """Test deleting non-existent WSJF item."""
        from uuid import uuid4

        non_existent_id = str(uuid4())

        response = api_client_with_db.delete(f"/api/items/{non_existent_id}")
        assert (
            response.status_code == 204
        )  # Our implementation returns 204 even if not found

    def test_create_batch_items(self, api_client_with_db, sample_wsjf_item_data):
        """Test creating multiple WSJF items in batch."""
        # Create batch data
        item1 = sample_wsjf_item_data
        item2 = sample_wsjf_item_data.copy()
        item2["subject"] = "Second Item"
        item3 = sample_wsjf_item_data.copy()
        item3["subject"] = "Third Item"

        batch_data = {"items": [item1, item2, item3]}

        response = api_client_with_db.post("/api/items/batch", json=batch_data)
        assert response.status_code == 201

        data = response.json()
        assert len(data) == 3

        # Verify all items have unique IDs
        ids = [item["id"] for item in data]
        assert len(set(ids)) == 3

    def test_generate_sample_data(self, api_client_with_db):
        """Test generating sample WSJF data."""
        response = api_client_with_db.get("/api/sample-data")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 3

        # Verify items have priorities
        priorities = [item["priority"] for item in data]
        assert set(priorities) == {1, 2, 3}

        # Verify all items have WSJF scores
        for item in data:
            assert "wsjf_score" in item
            assert item["wsjf_score"] > 0

    def test_get_stats(self, api_client_with_db, sample_wsjf_item_data):
        """Test getting WSJF statistics."""
        # Create some items first
        api_client_with_db.post("/api/items", json=sample_wsjf_item_data)

        response = api_client_with_db.get("/api/stats")
        assert response.status_code == 200

        data = response.json()
        assert "total_items" in data
        assert "avg_wsjf_score" in data
        assert "status_distribution" in data
        assert "team_distribution" in data


class TestExcelExportEndpoints:
    """Test Excel export functionality."""

    def test_export_excel_empty(self, api_client_with_db):
        """Test Excel export with no items."""
        response = api_client_with_db.get("/api/export/excel")
        assert response.status_code == 404  # No items to export

    def test_export_excel_with_items(self, api_client_with_db):
        """Test Excel export with items."""
        # Generate sample data first
        sample_response = api_client_with_db.get("/api/sample-data")
        assert sample_response.status_code == 200

        # Export Excel
        response = api_client_with_db.get("/api/export/excel")
        assert response.status_code == 200

        # Verify response headers
        assert (
            response.headers["content-type"]
            == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        assert "attachment" in response.headers.get("content-disposition", "")

    def test_export_excel_download_parameter(self, api_client_with_db):
        """Test Excel export with download parameter."""
        # Generate sample data first
        sample_response = api_client_with_db.get("/api/sample-data")
        assert sample_response.status_code == 200

        # Export Excel with download=true
        response = api_client_with_db.get("/api/export/excel?download=true")
        assert response.status_code == 200

        # Should have download headers
        assert "attachment" in response.headers.get("content-disposition", "")


class TestValidationAndErrorHandling:
    """Test validation and error handling."""

    def test_invalid_uuid_parameters(self, api_client_with_db):
        """Test endpoints with invalid UUID parameters."""
        invalid_uuid = "not-a-uuid"

        # Test various endpoints with invalid UUID
        endpoints = [
            f"/api/pis/{invalid_uuid}",
            f"/api/items/{invalid_uuid}",
            f"/api/pis/{invalid_uuid}/stats",
        ]

        for endpoint in endpoints:
            response = api_client_with_db.get(endpoint)
            assert response.status_code == 422  # Validation error

    def test_malformed_json(self, api_client_with_db):
        """Test endpoints with malformed JSON."""
        response = api_client_with_db.post(
            "/api/pis/",
            data="{ invalid json }",
            headers={"content-type": "application/json"},
        )
        assert response.status_code == 422

    def test_missing_required_fields(self, api_client_with_db):
        """Test creating items with missing required fields."""
        incomplete_data = {"description": "Missing required fields"}

        response = api_client_with_db.post("/api/items", json=incomplete_data)
        assert response.status_code == 422

        # Should have validation error details
        error_data = response.json()
        assert "detail" in error_data
