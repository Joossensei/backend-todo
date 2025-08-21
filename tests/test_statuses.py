import pytest
import logging
from tests.factories import StatusFactory
from app.schemas.status import StatusCreate, StatusUpdate, StatusPatch

logger = logging.getLogger(__name__)


class TestGetStatuses:
    """Test cases for statuses API endpoints"""

    @pytest.mark.asyncio
    async def test_get_statuses_no_data(self, auth_client):
        """Test getting statuses when database is empty"""
        response = await auth_client.get("/api/v1/statuses")
        assert response.status == 200
        data = await response.json()
        assert "statuses" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert "success" in data
        assert data["statuses"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["size"] == 0
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_get_statuses_with_pagination(self, auth_client, db_conn):
        """Test getting statuses with pagination parameters when data exists"""
        await StatusFactory.create_statuses_recursively(
            db_conn, auth_client.session.headers["User-Key"], 20
        )
        response = await auth_client.get("/api/v1/statuses?page=2&size=5")
        assert response.status == 200
        data = await response.json()
        assert data["page"] == 2
        assert data["size"] == 5  # Page size should be 5 when 20 statuses exist

    @pytest.mark.asyncio
    async def test_get_statuses_with_pagination_no_data(self, auth_client):
        """Test getting statuses with pagination parameters when no data exists"""
        response = await auth_client.get("/api/v1/statuses?page=2&size=5")
        assert response.status == 200
        data = await response.json()
        assert data["page"] == 2
        assert data["size"] == 0  # No statuses in database

    @pytest.mark.asyncio
    async def test_get_statuses_no_auth(self, client):
        """Test getting statuses without authentication"""
        response = await client.get("/api/v1/statuses")
        assert response.status == 401
        data = await response.json()
        assert data["detail"] == "Missing or invalid token"


class TestCreateStatus:
    @pytest.mark.asyncio
    async def test_create_status_success(self, auth_client):
        user_key = auth_client.session.headers["User-Key"]
        sample_status_data = StatusCreate(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=user_key,
            is_default=True,
        )
        response = await auth_client.post(
            "/api/v1/statuses", json=sample_status_data.model_dump()
        )
        assert response.status == 201
        data = await response.json()
        assert "key" in data
        assert "name" in data
        assert "color" in data
        assert "icon" in data
        assert "order" in data
        assert "created_at" in data
        assert data["name"] == sample_status_data.name
        assert data["color"] == sample_status_data.color
        assert data["order"] == sample_status_data.order
        assert data["icon"] == sample_status_data.icon
        assert data["user_key"] == sample_status_data.user_key


class TestCreateValidateStatus:
    @pytest.mark.asyncio
    async def test_create_status_empty_name(self, auth_client):
        """Test creating a status with invalid data"""
        invalid_data = {
            "name": " ",
            "color": "#FF0000",
            "icon": "fa-chevron-up",
            "order": 1,
            "user_key": auth_client.session.headers["User-Key"],
            "is_default": True,
        }  # Empty name
        response = await auth_client.post("/api/v1/statuses", json=invalid_data)
        assert response.status == 422  # Validation error
        data = await response.json()
        logger.info(data)
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Name is required"

    @pytest.mark.asyncio
    async def test_create_status_long_name(self, auth_client):
        """Test creating a status with invalid data"""
        invalid_data = {
            "name": "A" * 101,
            "color": "#FF0000",
            "icon": "fa-chevron-up",
            "order": 1,
            "user_key": auth_client.session.headers["User-Key"],
            "is_default": True,
        }  # Name exceeds 100 characters
        response = await auth_client.post("/api/v1/statuses", json=invalid_data)
        assert response.status == 422  # Validation error
        data = await response.json()
        logger.info(data)
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Name must be less than 100 characters"

    @pytest.mark.asyncio
    async def test_create_status_invalid_color_hex(self, auth_client):
        """Test creating a status with invalid data"""
        invalid_data = {
            "name": "High",
            "color": "#00FM",
            "icon": "fa-chevron-up",
            "order": 1,
            "user_key": auth_client.session.headers["User-Key"],
            "is_default": True,
        }  # Invalid hex color format
        response = await auth_client.post("/api/v1/statuses", json=invalid_data)
        assert response.status == 422  # Validation error
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Color must be a valid hex color"

    @pytest.mark.asyncio
    async def test_create_status_invalid_color_value(self, auth_client):
        """Test creating a status with invalid data"""
        invalid_data = {
            "name": "High",
            "color": "TESTING",
            "icon": "fa-chevron-up",
            "order": 1,
            "user_key": auth_client.session.headers["User-Key"],
            "is_default": True,
        }
        response = await auth_client.post("/api/v1/statuses", json=invalid_data)
        assert response.status == 422  # Validation error
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Color must start with #"

    @pytest.mark.asyncio
    async def test_create_status_invalid_color_length(self, auth_client):
        """Test creating a status with invalid data"""
        invalid_data = {
            "name": "High",
            "color": "#0000000",
            "icon": "fa-chevron-up",
            "order": 1,
            "user_key": auth_client.session.headers["User-Key"],
            "is_default": True,
        }
        response = await auth_client.post("/api/v1/statuses", json=invalid_data)
        assert response.status == 422  # Validation error
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Color must be less than 7 characters long"

    @pytest.mark.asyncio
    async def test_create_status_missing_required_fields(self, auth_client):
        """Test creating a status with missing required fields"""
        invalid_data = {"color": "#FF0000", "order": 1}
        response = await auth_client.post("/api/v1/statuses", json=invalid_data)
        assert response.status == 422  # Validation error
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "All fields are required"


class TestGetStatusByKey:
    @pytest.mark.asyncio
    async def test_get_status_by_key_success(self, auth_client):
        """Test getting a status by key successfully"""
        sample_status_data = StatusCreate(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
            is_default=True,
        )
        # First create a status
        create_response = await auth_client.post(
            "/api/v1/statuses", json=sample_status_data.model_dump()
        )
        if create_response.status != 201:
            data = await create_response.json()
            logger.error(data)
        assert create_response.status == 201
        created_status = await create_response.json()
        logger.info(created_status)
        status_key = created_status["key"]

        # Then get the status by key
        response = await auth_client.get(f"/api/v1/status/{status_key}")
        assert response.status == 200
        data = await response.json()
        assert data["key"] == status_key
        assert data["name"] == sample_status_data.name
        assert data["color"] == sample_status_data.color
        assert data["order"] == sample_status_data.order
        assert data["icon"] == sample_status_data.icon
        assert data["user_key"] == sample_status_data.user_key

    @pytest.mark.asyncio
    async def test_get_status_by_key_not_found(self, auth_client):
        """Test getting a status by non-existent key"""
        response = await auth_client.get("/api/v1/status/non-existent-key")
        assert response.status == 404
        data = await response.json()
        assert data["error"]["code"] == "not_found"
        assert data["error"]["message"] == "Status with key non-existent-key not found"


class TestUpdateStatus:
    @pytest.mark.asyncio
    async def test_update_status_success(self, auth_client):
        sample_status_data = StatusCreate(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
            is_default=True,
        )
        sample_status_update_data = StatusUpdate(
            name="Low",
            color="#00FF00",
            icon="fa-chevron-down",
            order=88,
            is_default=True,
        )
        # First create a status
        create_response = await auth_client.post(
            "/api/v1/statuses", json=sample_status_data.model_dump()
        )
        assert create_response.status == 201
        created_status = await create_response.json()
        status_key = created_status["key"]

        # Then update the status
        response = await auth_client.put(
            f"/api/v1/status/{status_key}",
            json=sample_status_update_data.model_dump(),
        )
        assert response.status == 200
        data = await response.json()
        assert data["name"] == sample_status_update_data.name
        assert data["color"] == sample_status_update_data.color
        assert data["order"] == sample_status_update_data.order
        assert data["icon"] == sample_status_update_data.icon

    @pytest.mark.asyncio
    async def test_update_status_not_found(self, auth_client):
        """Test updating a non-existent status"""
        sample_status_update_data = StatusUpdate(
            name="Low",
            color="#00FF00",
            icon="fa-chevron-down",
            order=2,
            is_default=True,
        )
        response = await auth_client.put(
            "/api/v1/status/non-existent-key",
            json=sample_status_update_data.model_dump(),
        )
        assert response.status == 404
        data = await response.json()
        assert data["error"]["code"] == "not_found"
        assert data["error"]["message"] == "Status with key non-existent-key not found"


class TestUpdateValidateStatus:
    @pytest.mark.asyncio
    async def test_update_status_empty_name(self, auth_client):
        """Test updating a status with invalid data"""
        sample_status_data = StatusCreate(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
            is_default=True,
        )
        # First create a status
        create_response = await auth_client.post(
            "/api/v1/statuses", json=sample_status_data.model_dump()
        )
        assert create_response.status == 201
        created_status = await create_response.json()
        status_key = created_status["key"]
        invalid_data = StatusUpdate(
            name=" ",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            is_default=True,
        )
        response = await auth_client.put(
            f"/api/v1/status/{status_key}",
            json=invalid_data.model_dump(),
        )
        assert response.status == 422  # Validation error
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Name is required"

    @pytest.mark.asyncio
    async def test_update_status_long_name(self, auth_client):
        """Test updating a status with invalid data"""
        sample_status_data = StatusCreate(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
            is_default=True,
        )
        # First create a status
        create_response = await auth_client.post(
            "/api/v1/statuses", json=sample_status_data.model_dump()
        )
        assert create_response.status == 201
        created_status = await create_response.json()
        status_key = created_status["key"]
        invalid_data = StatusUpdate(
            name="This is a long name that is greater than 100 characters for this it must be more than 100 characters so we type a very long string so it will fail",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            is_default=True,
        )
        response = await auth_client.put(
            f"/api/v1/status/{status_key}",
            json=invalid_data.model_dump(),
        )
        assert response.status == 422  # Validation error
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Name must be less than 100 characters"

    @pytest.mark.asyncio
    async def test_update_status_invalid_color(self, auth_client):
        """Test updating a status with invalid data"""
        sample_status_data = StatusCreate(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
            is_default=True,
        )
        # First create a status
        create_response = await auth_client.post(
            "/api/v1/statuses", json=sample_status_data.model_dump()
        )
        assert create_response.status == 201
        created_status = await create_response.json()
        status_key = created_status["key"]
        invalid_data = StatusUpdate(
            name="High",
            color="#00FM",
            icon="fa-chevron-up",
            order=1,
            is_default=True,
        )
        response = await auth_client.put(
            f"/api/v1/status/{status_key}",
            json=invalid_data.model_dump(),
        )
        assert response.status == 422  # Validation error
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Color must be a valid hex color"

    @pytest.mark.asyncio
    async def test_update_status_invalid_color_length(self, auth_client):
        """Test updating a status with invalid data"""
        sample_status_data = StatusCreate(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
            is_default=True,
        )
        # First create a status
        create_response = await auth_client.post(
            "/api/v1/statuses", json=sample_status_data.model_dump()
        )
        assert create_response.status == 201
        created_status = await create_response.json()
        status_key = created_status["key"]
        invalid_data = StatusUpdate(
            name="High",
            color="#0000000",
            icon="fa-chevron-up",
            order=1,
            is_default=True,
        )
        response = await auth_client.put(
            f"/api/v1/status/{status_key}",
            json=invalid_data.model_dump(),
        )
        assert response.status == 422  # Validation error
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Color must be less than 7 characters long"

    @pytest.mark.asyncio
    async def test_update_status_invalid_color_value(self, auth_client):
        """Test updating a status with invalid data"""
        sample_status_data = StatusCreate(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
            is_default=True,
            description="Test description",
        )
        # First create a status
        create_response = await auth_client.post(
            "/api/v1/statuses", json=sample_status_data.model_dump()
        )
        assert create_response.status == 201
        created_status = await create_response.json()
        status_key = created_status["key"]
        invalid_data = StatusUpdate(
            name="High",
            color="TESTING",
            icon="fa-chevron-up",
            order=1,
            is_default=True,
        )
        response = await auth_client.put(
            f"/api/v1/status/{status_key}",
            json=invalid_data.model_dump(),
        )
        assert response.status == 422  # Validation error
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Color must start with #"

    @pytest.mark.asyncio
    async def test_update_status_invalid_icon(self, auth_client):
        """Test updating a status with invalid data"""
        sample_status_data = StatusCreate(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
            is_default=True,
            description="Test description",
        )
        # First create a status
        create_response = await auth_client.post(
            "/api/v1/statuses", json=sample_status_data.model_dump()
        )
        assert create_response.status == 201
        created_status = await create_response.json()
        status_key = created_status["key"]
        invalid_data = StatusUpdate(
            name="High",
            color="#FF0000",
            icon=" ",
            order=1,
            is_default=True,
            description="Test description",
        )
        response = await auth_client.put(
            f"/api/v1/status/{status_key}",
            json=invalid_data.model_dump(),
        )
        assert response.status == 422  # Validation error
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Icon is required"

    @pytest.mark.asyncio
    async def test_update_status_invalid_order(self, auth_client):
        """Test updating a status with invalid data"""
        sample_status_data = StatusCreate(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
            description="Test description",
            is_default=True,
        )
        # First create a status
        create_response = await auth_client.post(
            "/api/v1/statuses", json=sample_status_data.model_dump()
        )
        assert create_response.status == 201
        created_status = await create_response.json()
        status_key = created_status["key"]
        invalid_data = StatusUpdate(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=0,
            is_default=True,
            description="Test description",
        )
        response = await auth_client.put(
            f"/api/v1/status/{status_key}",
            json=invalid_data.model_dump(),
        )
        assert response.status == 422  # Validation error
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Order must be greater than 0"


class TestPatchStatus:
    @pytest.mark.asyncio
    async def test_patch_status_success(self, auth_client):
        """Test patching a status successfully"""
        sample_status_data = StatusCreate(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
            is_default=True,
        )
        # First create a status
        create_response = await auth_client.post(
            "/api/v1/statuses", json=sample_status_data.model_dump()
        )
        assert create_response.status == 201
        created_status = await create_response.json()
        status_key = created_status["key"]

        # Then patch the status
        patch_data = StatusPatch(name="Patched Name", order=3)
        response = await auth_client.patch(
            f"/api/v1/status/{status_key}", json=patch_data.model_dump()
        )
        assert response.status == 200
        data = await response.json()
        assert data["name"] == "Patched Name"
        assert data["order"] == 3
        # Other fields should remain unchanged
        assert data["color"] == sample_status_data.color
        assert data["icon"] == sample_status_data.icon
        assert data["user_key"] == sample_status_data.user_key

    @pytest.mark.asyncio
    async def test_patch_status_not_found(self, auth_client):
        """Test patching a non-existent status"""
        patch_data = {"name": "Patched Name"}
        response = await auth_client.patch(
            "/api/v1/status/non-existent-key", json=patch_data
        )
        assert response.status == 404
        data = await response.json()
        assert data["error"]["code"] == "not_found"
        assert data["error"]["message"] == "Status with key non-existent-key not found"


class TestPatchValidateStatus:
    @pytest.mark.asyncio
    async def test_patch_status_empty_name(self, auth_client):
        """Test patching a status with invalid data"""
        sample_status_data = StatusCreate(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
            description="Test description",
            is_default=True,
        )
        # First create a status
        create_response = await auth_client.post(
            "/api/v1/statuses", json=sample_status_data.model_dump()
        )
        assert create_response.status == 201
        created_status = await create_response.json()
        status_key = created_status["key"]
        invalid_data = StatusPatch(name=" ")
        response = await auth_client.patch(
            f"/api/v1/status/{status_key}", json=invalid_data.model_dump()
        )
        assert response.status == 422  # Validation error
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Name is required"

    @pytest.mark.asyncio
    async def test_patch_status_long_name(self, auth_client):
        """Test patching a status with invalid data"""
        sample_status_data = StatusCreate(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
            description="Test description",
            is_default=True,
        )
        # First create a status
        create_response = await auth_client.post(
            "/api/v1/statuses", json=sample_status_data.model_dump()
        )
        assert create_response.status == 201
        created_status = await create_response.json()
        status_key = created_status["key"]
        invalid_data = StatusPatch(
            name="This is a long name that is greater than 100 characters for this it must be more than 100 characters so we type a very long string so it will fail",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
        )
        response = await auth_client.patch(
            f"/api/v1/status/{status_key}", json=invalid_data.model_dump()
        )
        assert response.status == 422  # Validation error
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Name must be less than 100 characters"

    @pytest.mark.asyncio
    async def test_patch_status_invalid_color(self, auth_client):
        """Test patching a status with invalid data"""
        sample_status_data = StatusCreate(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
            description="Test description",
            is_default=True,
        )
        # First create a status
        create_response = await auth_client.post(
            "/api/v1/statuses", json=sample_status_data.model_dump()
        )
        assert create_response.status == 201
        created_status = await create_response.json()
        status_key = created_status["key"]
        invalid_data = StatusPatch(
            name="High",
            color="#00FM",
            icon="fa-chevron-up",
            order=1,
        )
        response = await auth_client.patch(
            f"/api/v1/status/{status_key}", json=invalid_data.model_dump()
        )
        assert response.status == 422  # Validation error
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Color must be a valid hex color"

    @pytest.mark.asyncio
    async def test_patch_status_invalid_color_length(self, auth_client):
        """Test patching a status with invalid data"""
        sample_status_data = StatusCreate(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
            description="Test description",
            is_default=True,
        )
        # First create a status
        create_response = await auth_client.post(
            "/api/v1/statuses", json=sample_status_data.model_dump()
        )
        assert create_response.status == 201
        created_status = await create_response.json()
        status_key = created_status["key"]
        invalid_data = StatusPatch(
            name="High",
            color="#0000000",
            icon="fa-chevron-up",
            order=1,
        )
        response = await auth_client.patch(
            f"/api/v1/status/{status_key}", json=invalid_data.model_dump()
        )
        assert response.status == 422  # Validation error
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Color must be less than 7 characters long"

    @pytest.mark.asyncio
    async def test_patch_status_invalid_color_value(self, auth_client):
        """Test patching a status with invalid data"""
        sample_status_data = StatusCreate(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
            description="Test description",
            is_default=True,
        )
        # First create a status
        create_response = await auth_client.post(
            "/api/v1/statuses", json=sample_status_data.model_dump()
        )
        assert create_response.status == 201
        created_status = await create_response.json()
        status_key = created_status["key"]
        invalid_data = StatusPatch(
            name="High",
            color="TESTING",
            icon="fa-chevron-up",
            order=1,
        )
        response = await auth_client.patch(
            f"/api/v1/status/{status_key}", json=invalid_data.model_dump()
        )
        assert response.status == 422  # Validation error
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Color must start with #"

    @pytest.mark.asyncio
    async def test_patch_status_invalid_icon(self, auth_client):
        """Test patching a status with invalid data"""
        sample_status_data = StatusCreate(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
            description="Test description",
            is_default=True,
        )
        # First create a status
        create_response = await auth_client.post(
            "/api/v1/statuses", json=sample_status_data.model_dump()
        )
        assert create_response.status == 201
        created_status = await create_response.json()
        status_key = created_status["key"]
        invalid_data = StatusPatch(
            name="High",
            color="#FF0000",
            icon=" ",
            order=1,
        )
        response = await auth_client.patch(
            f"/api/v1/status/{status_key}", json=invalid_data.model_dump()
        )
        assert response.status == 422  # Validation error
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Icon is required"

    @pytest.mark.asyncio
    async def test_patch_status_invalid_order(self, auth_client):
        """Test patching a status with invalid data"""
        sample_status_data = StatusCreate(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
            description="Test description",
            is_default=True,
        )
        # First create a status
        create_response = await auth_client.post(
            "/api/v1/statuses", json=sample_status_data.model_dump()
        )
        assert create_response.status == 201
        created_status = await create_response.json()
        status_key = created_status["key"]
        invalid_data = StatusPatch(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=0,
        )
        response = await auth_client.patch(
            f"/api/v1/status/{status_key}", json=invalid_data.model_dump()
        )
        assert response.status == 422  # Validation error
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Order must be greater than 0"


class TestDeleteStatus:
    @pytest.mark.asyncio
    async def test_delete_status_success(self, auth_client):
        """Test deleting a status successfully"""
        sample_status_data = StatusCreate(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
            description="Test description",
            is_default=True,
        )
        # First create a status
        create_response = await auth_client.post(
            "/api/v1/statuses", json=sample_status_data.model_dump()
        )
        assert create_response.status == 201
        created_status = await create_response.json()
        status_key = created_status["key"]

        # Then delete the status
        response = await auth_client.delete(f"/api/v1/status/{status_key}")
        assert response.status == 204

        # Verify the status is deleted
        get_response = await auth_client.get(f"/api/v1/status/{status_key}")
        assert get_response.status == 404

    @pytest.mark.asyncio
    async def test_delete_status_not_found(self, auth_client):
        """Test deleting a non-existent status"""
        response = await auth_client.delete("/api/v1/status/non-existent-key")
        assert response.status == 404
        data = await response.json()
        assert data["error"]["code"] == "not_found"
        assert data["error"]["message"] == "Status with key non-existent-key not found"


class TestGetStatusesWithData:
    @pytest.mark.asyncio
    async def test_get_statuses_with_data(self, auth_client):
        """Test getting statuses when there is data in the database"""
        # Create multiple statuses
        for i in range(3):
            status_data = StatusCreate(
                name=f"Status {i+1}",
                color="#FF0000",
                icon="fa-chevron-up",
                order=i + 1,
                user_key=auth_client.session.headers["User-Key"],
                description="Test description",
                is_default=True,
            )
            response = await auth_client.post(
                "/api/v1/statuses", json=status_data.model_dump()
            )
            assert response.status == 201

        # Get all statuses
        response = await auth_client.get("/api/v1/statuses")
        assert response.status == 200
        data = await response.json()
        assert len(data["statuses"]) == 3
        assert data["total"] == 3
        assert data["success"] is True


class TestReorderStatuses:
    @pytest.mark.asyncio
    async def test_reorder_statuses_success(self, auth_client):
        """Test reordering statuses successfully"""
        # Create multiple statuses
        statuses = []
        for i in range(3):
            status_data = StatusCreate(
                name=f"Status {i+1}",
                color="#FF0000",
                icon="fa-chevron-up",
                order=i + 1,
                user_key=auth_client.session.headers["User-Key"],
                description="Test description",
                is_default=True,
            )
            response = await auth_client.post(
                "/api/v1/statuses", json=status_data.model_dump()
            )
            assert response.status == 201
            statuses.append(await response.json())

        # Verify initial order
        response = await auth_client.get("/api/v1/statuses")
        assert response.status == 200
        data = await response.json()
        assert data["statuses"][0]["order"] == 1
        assert data["statuses"][1]["order"] == 2
        assert data["statuses"][2]["order"] == 3

        # Reorder: move status from order 1 to order 3
        reorder_data = {"fromOrder": 1, "toOrder": 3}
        response = await auth_client.patch(
            f"/api/v1/status/{statuses[0]['key']}/reorder", json=reorder_data
        )
        assert response.status == 200
        data = await response.json()
        assert data["success"] is True
        assert len(data["statuses"]) == 3

        # Verify the new order
        # The status that was at order 1 should now be at order 3
        # The statuses that were at orders 2 and 3 should now be at orders 1 and 2
        statuses_by_order = {p["order"]: p for p in data["statuses"]}
        assert statuses_by_order[1]["name"] == "Status 2"
        assert statuses_by_order[2]["name"] == "Status 3"
        assert statuses_by_order[3]["name"] == "Status 1"

    @pytest.mark.asyncio
    async def test_reorder_statuses_move_up(self, auth_client):
        """Test reordering statuses by moving up"""
        # Create multiple statuses
        statuses = []
        for i in range(3):
            status_data = StatusCreate(
                name=f"Status {i+1}",
                color="#FF0000",
                icon="fa-chevron-up",
                order=i + 1,
                user_key=auth_client.session.headers["User-Key"],
                description="Test description",
                is_default=True,
            )
            response = await auth_client.post(
                "/api/v1/statuses", json=status_data.model_dump()
            )
            assert response.status == 201
            statuses.append(await response.json())

        # Reorder: move status from order 3 to order 1
        reorder_data = {"fromOrder": 3, "toOrder": 1}
        response = await auth_client.patch(
            f"/api/v1/status/{statuses[2]['key']}/reorder", json=reorder_data
        )
        assert response.status == 200
        data = await response.json()
        assert data["success"] is True

        # Verify the new order
        statuses_by_order = {p["order"]: p for p in data["statuses"]}
        assert statuses_by_order[1]["name"] == "Status 3"
        assert statuses_by_order[2]["name"] == "Status 1"
        assert statuses_by_order[3]["name"] == "Status 2"

    @pytest.mark.asyncio
    async def test_reorder_statuses_same_order(self, auth_client):
        """Test reordering statuses with same from and to order"""
        # Create a status
        status_data = StatusCreate(
            name="Test Status",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
            description="Test description",
            is_default=True,
        )
        response = await auth_client.post(
            "/api/v1/statuses", json=status_data.model_dump()
        )
        assert response.status == 201

        created_status = await response.json()
        # Reorder: same order (should be a no-op)
        reorder_data = {"fromOrder": 1, "toOrder": 1}
        response = await auth_client.patch(
            f"/api/v1/status/{created_status['key']}/reorder", json=reorder_data
        )
        assert response.status == 200
        data = await response.json()
        assert data["success"] is True
        assert len(data["statuses"]) == 1
        assert data["statuses"][0]["order"] == 1

    @pytest.mark.asyncio
    async def test_reorder_statuses_invalid_from_order(self, auth_client):
        """Test reordering with invalid from order"""
        # Create a status
        status_data = StatusCreate(
            name="Test Status",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
            description="Test description",
            is_default=True,
        )
        response = await auth_client.post(
            "/api/v1/statuses", json=status_data.model_dump()
        )
        assert response.status == 201

        created_status = await response.json()
        # Try to reorder with non-existent from order
        reorder_data = {"fromOrder": 999, "toOrder": 1}
        response = await auth_client.patch(
            f"/api/v1/status/{created_status['key']}/reorder", json=reorder_data
        )
        assert response.status == 404
        data = await response.json()
        assert data["error"]["code"] == "not_found"
        assert "Status with order 999 not found" in data["error"]["message"]

    @pytest.mark.asyncio
    async def test_reorder_statuses_invalid_to_order(self, auth_client):
        """Test reordering with invalid to order"""
        # Create a status
        status_data = StatusCreate(
            name="Test Status",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
            description="Test description",
            is_default=True,
        )
        response = await auth_client.post(
            "/api/v1/statuses", json=status_data.model_dump()
        )
        assert response.status == 201

        created_status = await response.json()
        # Try to reorder with invalid to order
        reorder_data = {"fromOrder": 1, "toOrder": 999}
        response = await auth_client.patch(
            f"/api/v1/status/{created_status['key']}/reorder", json=reorder_data
        )
        assert response.status == 422
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert "Target order must be between 1 and 1" in data["error"]["message"]

    @pytest.mark.asyncio
    async def test_reorder_statuses_no_auth(self, client):
        """Test reordering statuses without authentication"""
        reorder_data = {"fromOrder": 1, "toOrder": 2}
        response = await client.patch(
            "/api/v1/status/some-key/reorder", json=reorder_data
        )
        assert response.status == 401
        data = await response.json()
        assert data["detail"] == "Missing or invalid token"

    @pytest.mark.asyncio
    async def test_reorder_statuses_invalid_request_body(self, auth_client):
        """Test reordering with invalid request body"""
        # Missing required fields
        reorder_data = {"fromOrder": 1}  # Missing toOrder
        response = await auth_client.patch(
            "/api/v1/status/key/reorder", json=reorder_data
        )
        assert response.status == 422
        data = await response.json()
        assert data["error"]["code"] == "validation_error"

        # Invalid field types
        reorder_data = {"fromOrder": "invalid", "toOrder": 2}
        response = await auth_client.patch(
            "/api/v1/status/key/reorder", json=reorder_data
        )
        assert response.status == 422
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
