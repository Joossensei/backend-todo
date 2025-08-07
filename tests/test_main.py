from fastapi.testclient import TestClient


class TestMainEndpoints:
    """Test cases for main application endpoints"""

    def test_root_endpoint(self, client: TestClient):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert data["message"] == "Welcome to Todo API"
        assert data["docs"] == "/docs"

    def test_health_endpoint(self, client: TestClient):
        """Test the health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert data["status"] == "healthy"
        assert isinstance(data["timestamp"], str)

    def test_docs_endpoint(self, client: TestClient):
        """Test that the docs endpoint is accessible"""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_endpoint(self, client: TestClient):
        """Test that the OpenAPI schema endpoint is accessible"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
