import pytest


class TestMainEndpoints:
    """Test cases for main application endpoints"""

    @pytest.mark.asyncio
    async def test_root_endpoint(self, client):
        """Test the root endpoint"""
        response = await client.get("/")
        assert response.status == 200
        data = await response.json()
        assert "message" in data
        assert "version" in data
        assert data["message"] == "Welcome to Todo API"

    @pytest.mark.asyncio
    async def test_health_endpoint(self, client):
        """Test the health endpoint"""
        response = await client.get("/health")
        assert response.status == 200
        data = await response.json()
        assert "status" in data
        assert data["status"] == "OK"
