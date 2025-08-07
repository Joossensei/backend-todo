from fastapi.testclient import TestClient


class TestPrioritiesAPI:
    """Test cases for priorities API endpoints"""

    def test_get_priorities_empty(self, client: TestClient):
        """Test getting priorities when database is empty"""
        response = client.get("/api/v1/priorities/")
        assert response.status_code == 200
        data = response.json()
        assert "priorities" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert "success" in data
        assert data["priorities"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["size"] == 0
        assert data["success"] is True

    def test_get_priorities_with_pagination(self, client: TestClient):
        """Test getting priorities with pagination parameters"""
        response = client.get("/api/v1/priorities/?page=2&size=5")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert data["size"] == 0  # No priorities in database

    def test_create_priority_success(self, client: TestClient, sample_priority_data):
        """Test creating a priority successfully"""
        response = client.post("/api/v1/priorities/", json=sample_priority_data)
        assert response.status_code == 200
        data = response.json()
        assert "key" in data
        assert "name" in data
        assert "color" in data
        assert "order" in data
        assert "created_at" in data
        assert data["name"] == sample_priority_data["name"]
        assert data["color"] == sample_priority_data["color"]
        assert data["order"] == sample_priority_data["order"]

    def test_create_priority_invalid_data(self, client: TestClient):
        """Test creating a priority with invalid data"""
        invalid_data = {"name": "", "color": "#FF0000", "level": 1}  # Empty name
        response = client.post("/api/v1/priorities/", json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_create_priority_missing_required_fields(self, client: TestClient):
        """Test creating a priority with missing required fields"""
        invalid_data = {"color": "#FF0000", "level": 1}
        response = client.post("/api/v1/priorities/", json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_get_priority_by_key_success(
        self, client: TestClient, sample_priority_data
    ):
        """Test getting a priority by key successfully"""
        # First create a priority
        create_response = client.post("/api/v1/priorities/", json=sample_priority_data)
        assert create_response.status_code == 200
        created_priority = create_response.json()
        priority_key = created_priority["key"]

        # Then get the priority by key
        response = client.get(f"/api/v1/priorities/{priority_key}")
        assert response.status_code == 200
        data = response.json()
        assert data["key"] == priority_key
        assert data["name"] == sample_priority_data["name"]

    def test_get_priority_by_key_not_found(self, client: TestClient):
        """Test getting a priority by non-existent key"""
        response = client.get("/api/v1/priorities/non-existent-key")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"]

    def test_update_priority_success(
        self, client: TestClient, sample_priority_data, sample_priority_update_data
    ):
        """Test updating a priority successfully"""
        # First create a priority
        create_response = client.post("/api/v1/priorities/", json=sample_priority_data)
        assert create_response.status_code == 200
        created_priority = create_response.json()
        priority_key = created_priority["key"]

        # Then update the priority
        response = client.put(
            f"/api/v1/priorities/{priority_key}", json=sample_priority_update_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_priority_update_data["name"]
        assert data["color"] == sample_priority_update_data["color"]
        assert data["order"] == sample_priority_update_data["order"]

    def test_update_priority_not_found(
        self, client: TestClient, sample_priority_update_data
    ):
        """Test updating a non-existent priority"""
        response = client.put(
            "/api/v1/priorities/non-existent-key", json=sample_priority_update_data
        )
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"]

    def test_patch_priority_success(self, client: TestClient, sample_priority_data):
        """Test patching a priority successfully"""
        # First create a priority
        create_response = client.post("/api/v1/priorities/", json=sample_priority_data)
        assert create_response.status_code == 200
        created_priority = create_response.json()
        priority_key = created_priority["key"]

        # Then patch the priority
        patch_data = {"name": "Patched Name", "order": 3}
        response = client.patch(f"/api/v1/priorities/{priority_key}", json=patch_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Patched Name"
        assert data["order"] == 3
        # Other fields should remain unchanged
        assert data["color"] == sample_priority_data["color"]

    def test_patch_priority_not_found(self, client: TestClient):
        """Test patching a non-existent priority"""
        patch_data = {"name": "Patched Name"}
        response = client.patch("/api/v1/priorities/non-existent-key", json=patch_data)
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"]

    def test_delete_priority_success(self, client: TestClient, sample_priority_data):
        """Test deleting a priority successfully"""
        # First create a priority
        create_response = client.post("/api/v1/priorities/", json=sample_priority_data)
        assert create_response.status_code == 200
        created_priority = create_response.json()
        priority_key = created_priority["key"]

        # Then delete the priority
        response = client.delete(f"/api/v1/priorities/{priority_key}")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "deleted successfully" in data["message"]

        # Verify the priority is deleted
        get_response = client.get(f"/api/v1/priorities/{priority_key}")
        assert get_response.status_code == 404

    def test_delete_priority_not_found(self, client: TestClient):
        """Test deleting a non-existent priority"""
        response = client.delete("/api/v1/priorities/non-existent-key")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"]

    def test_get_priorities_with_data(self, client: TestClient, sample_priority_data):
        """Test getting priorities when there is data in the database"""
        # Create multiple priorities
        for i in range(3):
            priority_data = sample_priority_data.copy()
            priority_data["name"] = f"Priority {i+1}"
            priority_data["level"] = i + 1
            response = client.post("/api/v1/priorities/", json=priority_data)
            assert response.status_code == 200

        # Get all priorities
        response = client.get("/api/v1/priorities/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["priorities"]) == 3
        assert data["total"] == 3
        assert data["success"] is True
