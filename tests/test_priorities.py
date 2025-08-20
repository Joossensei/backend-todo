import pytest
import logging
from tests.factories import PriorityFactory
from app.schemas.priority import PriorityCreate, PriorityUpdate, PriorityPatch

logger = logging.getLogger(__name__)


class TestGetPriorities:
    """Test cases for priorities API endpoints"""

    @pytest.mark.asyncio
    async def test_get_priorities_no_data(self, auth_client):
        """Test getting priorities when database is empty"""
        response = await auth_client.get("/api/v1/priorities")
        assert response.status == 200
        data = await response.json()
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

    @pytest.mark.asyncio
    async def test_get_priorities_with_pagination(self, auth_client, db_conn):
        """Test getting priorities with pagination parameters"""
        await PriorityFactory.create_priorities_recursively(
            db_conn, auth_client.session.headers["User-Key"], 20
        )
        response = await auth_client.get("/api/v1/priorities?page=2&size=5")
        assert response.status == 200
        data = await response.json()
        assert data["page"] == 2
        assert data["size"] == 5  # No priorities in database

    @pytest.mark.asyncio
    async def test_get_priorities_with_pagination_no_data(self, auth_client):
        """Test getting priorities with pagination parameters"""
        response = await auth_client.get("/api/v1/priorities?page=2&size=5")
        assert response.status == 200
        data = await response.json()
        assert data["page"] == 2
        assert data["size"] == 0  # No priorities in database

    @pytest.mark.asyncio
    async def test_get_priorities_no_auth(self, client):
        """Test getting priorities with pagination parameters"""
        response = await client.get("/api/v1/priorities")
        assert response.status == 401
        data = await response.json()
        assert data["detail"] == "Missing or invalid token"


class TestCreatePriority:
    @pytest.mark.asyncio
    async def test_create_priority_success(self, auth_client):
        user_key = auth_client.session.headers["User-Key"]
        sample_priority_data = PriorityCreate(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=user_key,
        )
        """Test creating a priority successfully"""
        response = await auth_client.post(
            "/api/v1/priorities", json=sample_priority_data.model_dump()
        )
        assert response.status == 201
        data = await response.json()
        assert "key" in data
        assert "name" in data
        assert "color" in data
        assert "icon" in data
        assert "order" in data
        assert "created_at" in data
        assert data["name"] == sample_priority_data.name
        assert data["color"] == sample_priority_data.color
        assert data["order"] == sample_priority_data.order
        assert data["icon"] == sample_priority_data.icon
        assert data["user_key"] == sample_priority_data.user_key


class TestCreateValidatePriority:
    @pytest.mark.asyncio
    async def test_create_priority_empty_name(self, auth_client):
        """Test creating a priority with invalid data"""
        invalid_data = PriorityCreate(
            name=" ",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
        )  # Empty name
        response = await auth_client.post(
            "/api/v1/priorities", json=invalid_data.model_dump()
        )
        assert response.status == 422  # Validation error
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Name is required"

    @pytest.mark.asyncio
    async def test_create_priority_long_name(self, auth_client):
        """Test creating a priority with invalid data"""
        invalid_data = PriorityCreate(
            name="This is a long name that is greater than 100 characters for this it must be more than 100 characters so we type a very long string so it will fail",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
        )  # Empty name
        response = await auth_client.post(
            "/api/v1/priorities", json=invalid_data.model_dump()
        )
        assert response.status == 422  # Validation error
        data = await response.json()
        logger.info(data)
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Name must be less than 100 characters"

    @pytest.mark.asyncio
    async def test_create_priority_invalid_color_hex(self, auth_client):
        """Test creating a priority with invalid data"""
        invalid_data = PriorityCreate(
            name="High",
            color="#00FM",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
        )  # Empty color
        response = await auth_client.post(
            "/api/v1/priorities", json=invalid_data.model_dump()
        )
        assert response.status == 422  # Validation error
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Color must be a valid hex color"

    @pytest.mark.asyncio
    async def test_create_priority_invalid_color_value(self, auth_client):
        """Test creating a priority with invalid data"""
        invalid_data = PriorityCreate(
            name="High",
            color="TESTING",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
        )  # Empty color
        response = await auth_client.post(
            "/api/v1/priorities", json=invalid_data.model_dump()
        )
        assert response.status == 422  # Validation error
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Color must start with #"

    @pytest.mark.asyncio
    async def test_create_priority_invalid_color_length(self, auth_client):
        """Test creating a priority with invalid data"""
        invalid_data = {
            "name": "High",
            "color": "#0000000",
            "icon": "fa-chevron-up",
            "order": 1,
            "user_key": auth_client.session.headers["User-Key"],
        }
        response = await auth_client.post("/api/v1/priorities", json=invalid_data)
        assert response.status == 422  # Validation error
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Color must be less than 7 characters long"

    @pytest.mark.asyncio
    async def test_create_priority_missing_required_fields(self, auth_client):
        """Test creating a priority with missing required fields"""
        invalid_data = {"color": "#FF0000", "order": 1}
        response = await auth_client.post("/api/v1/priorities", json=invalid_data)
        assert response.status == 422  # Validation error
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "All fields are required"


class TestGetPriorityByKey:
    @pytest.mark.asyncio
    async def test_get_priority_by_key_success(self, auth_client):
        """Test getting a priority by key successfully"""
        sample_priority_data = PriorityCreate(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
        )
        # First create a priority
        create_response = await auth_client.post(
            "/api/v1/priorities", json=sample_priority_data.model_dump()
        )
        if create_response.status != 201:
            data = await create_response.json()
            logger.error(data)
        assert create_response.status == 201
        created_priority = await create_response.json()
        logger.info(created_priority)
        priority_key = created_priority["key"]

        # Then get the priority by key
        response = await auth_client.get(f"/api/v1/priority/{priority_key}")
        assert response.status == 200
        data = await response.json()
        assert data["key"] == priority_key
        assert data["name"] == sample_priority_data.name
        assert data["color"] == sample_priority_data.color
        assert data["order"] == sample_priority_data.order
        assert data["icon"] == sample_priority_data.icon
        assert data["user_key"] == sample_priority_data.user_key

    @pytest.mark.asyncio
    async def test_get_priority_by_key_not_found(self, auth_client):
        """Test getting a priority by non-existent key"""
        response = await auth_client.get("/api/v1/priority/non-existent-key")
        assert response.status == 404
        data = await response.json()
        assert data["error"]["code"] == "not_found"
        assert (
            data["error"]["message"] == "Priority with key non-existent-key not found"
        )


class TestUpdatePriority:
    @pytest.mark.asyncio
    async def test_update_priority_success(self, auth_client):
        sample_priority_data = PriorityCreate(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
        )
        sample_priority_update_data = PriorityUpdate(
            name="Low",
            color="#00FF00",
            icon="fa-chevron-down",
            order=88,
        )
        """Test updating a priority successfully"""
        # First create a priority
        create_response = await auth_client.post(
            "/api/v1/priorities", json=sample_priority_data.model_dump()
        )
        assert create_response.status == 201
        created_priority = await create_response.json()
        priority_key = created_priority["key"]

        # Then update the priority
        response = await auth_client.put(
            f"/api/v1/priority/{priority_key}",
            json=sample_priority_update_data.model_dump(),
        )
        assert response.status == 200
        data = await response.json()
        assert data["name"] == sample_priority_update_data.name
        assert data["color"] == sample_priority_update_data.color
        assert data["order"] == sample_priority_update_data.order
        assert data["icon"] == sample_priority_update_data.icon

    @pytest.mark.asyncio
    async def test_update_priority_not_found(self, auth_client):
        """Test updating a non-existent priority"""
        sample_priority_update_data = PriorityUpdate(
            name="Low",
            color="#00FF00",
            icon="fa-chevron-down",
            order=2,
        )
        response = await auth_client.put(
            "/api/v1/priority/non-existent-key",
            json=sample_priority_update_data.model_dump(),
        )
        assert response.status == 404
        data = await response.json()
        assert data["error"]["code"] == "not_found"
        assert (
            data["error"]["message"] == "Priority with key non-existent-key not found"
        )


class TestUpdateValidatePriority:
    @pytest.mark.asyncio
    async def test_update_priority_empty_name(self, auth_client):
        """Test updating a priority with invalid data"""
        sample_priority_data = PriorityCreate(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
        )
        # First create a priority
        create_response = await auth_client.post(
            "/api/v1/priorities", json=sample_priority_data.model_dump()
        )
        assert create_response.status == 201
        created_priority = await create_response.json()
        priority_key = created_priority["key"]
        invalid_data = PriorityUpdate(
            name=" ",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
        )
        response = await auth_client.put(
            f"/api/v1/priority/{priority_key}",
            json=invalid_data.model_dump(),
        )
        assert response.status == 422  # Validation error
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Name is required"

    @pytest.mark.asyncio
    async def test_update_priority_long_name(self, auth_client):
        """Test updating a priority with invalid data"""
        sample_priority_data = PriorityCreate(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
        )
        # First create a priority
        create_response = await auth_client.post(
            "/api/v1/priorities", json=sample_priority_data.model_dump()
        )
        assert create_response.status == 201
        created_priority = await create_response.json()
        priority_key = created_priority["key"]
        invalid_data = PriorityUpdate(
            name="This is a long name that is greater than 100 characters for this it must be more than 100 characters so we type a very long string so it will fail",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
        )
        response = await auth_client.put(
            f"/api/v1/priority/{priority_key}",
            json=invalid_data.model_dump(),
        )
        assert response.status == 422  # Validation error
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Name must be less than 100 characters"

    @pytest.mark.asyncio
    async def test_update_priority_invalid_color(self, auth_client):
        """Test updating a priority with invalid data"""
        sample_priority_data = PriorityCreate(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
        )
        # First create a priority
        create_response = await auth_client.post(
            "/api/v1/priorities", json=sample_priority_data.model_dump()
        )
        assert create_response.status == 201
        created_priority = await create_response.json()
        priority_key = created_priority["key"]
        invalid_data = PriorityUpdate(
            name="High",
            color="#00FM",
            icon="fa-chevron-up",
            order=1,
        )
        response = await auth_client.put(
            f"/api/v1/priority/{priority_key}",
            json=invalid_data.model_dump(),
        )
        assert response.status == 422  # Validation error
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Color must be a valid hex color"

    @pytest.mark.asyncio
    async def test_update_priority_invalid_color_length(self, auth_client):
        """Test updating a priority with invalid data"""
        sample_priority_data = PriorityCreate(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
        )
        # First create a priority
        create_response = await auth_client.post(
            "/api/v1/priorities", json=sample_priority_data.model_dump()
        )
        assert create_response.status == 201
        created_priority = await create_response.json()
        priority_key = created_priority["key"]
        invalid_data = PriorityUpdate(
            name="High",
            color="#0000000",
            icon="fa-chevron-up",
            order=1,
        )
        response = await auth_client.put(
            f"/api/v1/priority/{priority_key}",
            json=invalid_data.model_dump(),
        )
        assert response.status == 422  # Validation error
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Color must be less than 7 characters long"

    @pytest.mark.asyncio
    async def test_update_priority_invalid_color_value(self, auth_client):
        """Test updating a priority with invalid data"""
        sample_priority_data = PriorityCreate(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
        )
        # First create a priority
        create_response = await auth_client.post(
            "/api/v1/priorities", json=sample_priority_data.model_dump()
        )
        assert create_response.status == 201
        created_priority = await create_response.json()
        priority_key = created_priority["key"]
        invalid_data = PriorityUpdate(
            name="High",
            color="TESTING",
            icon="fa-chevron-up",
            order=1,
        )
        response = await auth_client.put(
            f"/api/v1/priority/{priority_key}",
            json=invalid_data.model_dump(),
        )
        assert response.status == 422  # Validation error
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Color must start with #"

    @pytest.mark.asyncio
    async def test_update_priority_invalid_icon(self, auth_client):
        """Test updating a priority with invalid data"""
        sample_priority_data = PriorityCreate(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
        )
        # First create a priority
        create_response = await auth_client.post(
            "/api/v1/priorities", json=sample_priority_data.model_dump()
        )
        assert create_response.status == 201
        created_priority = await create_response.json()
        priority_key = created_priority["key"]
        invalid_data = PriorityUpdate(
            name="High",
            color="#FF0000",
            icon=" ",
            order=1,
        )
        response = await auth_client.put(
            f"/api/v1/priority/{priority_key}",
            json=invalid_data.model_dump(),
        )
        assert response.status == 422  # Validation error
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Icon is required"

    @pytest.mark.asyncio
    async def test_update_priority_invalid_order(self, auth_client):
        """Test updating a priority with invalid data"""
        sample_priority_data = PriorityCreate(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
        )
        # First create a priority
        create_response = await auth_client.post(
            "/api/v1/priorities", json=sample_priority_data.model_dump()
        )
        assert create_response.status == 201
        created_priority = await create_response.json()
        priority_key = created_priority["key"]
        invalid_data = PriorityUpdate(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=0,
        )
        response = await auth_client.put(
            f"/api/v1/priority/{priority_key}",
            json=invalid_data.model_dump(),
        )
        assert response.status == 422  # Validation error
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Order must be greater than 0"


class TestPatchPriority:
    @pytest.mark.asyncio
    async def test_patch_priority_success(self, auth_client):
        """Test patching a priority successfully"""
        sample_priority_data = PriorityCreate(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
        )
        # First create a priority
        create_response = await auth_client.post(
            "/api/v1/priorities", json=sample_priority_data.model_dump()
        )
        assert create_response.status == 201
        created_priority = await create_response.json()
        priority_key = created_priority["key"]

        # Then patch the priority
        patch_data = PriorityPatch(name="Patched Name", order=3)
        response = await auth_client.patch(
            f"/api/v1/priority/{priority_key}", json=patch_data.model_dump()
        )
        assert response.status == 200
        data = await response.json()
        assert data["name"] == "Patched Name"
        assert data["order"] == 3
        # Other fields should remain unchanged
        assert data["color"] == sample_priority_data.color
        assert data["icon"] == sample_priority_data.icon
        assert data["user_key"] == sample_priority_data.user_key

    @pytest.mark.asyncio
    async def test_patch_priority_not_found(self, auth_client):
        """Test patching a non-existent priority"""
        patch_data = {"name": "Patched Name"}
        response = await auth_client.patch(
            "/api/v1/priority/non-existent-key", json=patch_data
        )
        assert response.status == 404
        data = await response.json()
        assert data["error"]["code"] == "not_found"
        assert (
            data["error"]["message"] == "Priority with key non-existent-key not found"
        )


class TestPatchValidatePriority:
    @pytest.mark.asyncio
    async def test_patch_priority_empty_name(self, auth_client):
        """Test patching a priority with invalid data"""
        sample_priority_data = PriorityCreate(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
        )
        # First create a priority
        create_response = await auth_client.post(
            "/api/v1/priorities", json=sample_priority_data.model_dump()
        )
        assert create_response.status == 201
        created_priority = await create_response.json()
        priority_key = created_priority["key"]
        invalid_data = PriorityPatch(name=" ")
        response = await auth_client.patch(
            f"/api/v1/priority/{priority_key}", json=invalid_data.model_dump()
        )
        assert response.status == 422  # Validation error
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Name is required"

    @pytest.mark.asyncio
    async def test_patch_priority_long_name(self, auth_client):
        """Test patching a priority with invalid data"""
        sample_priority_data = PriorityCreate(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
        )
        # First create a priority
        create_response = await auth_client.post(
            "/api/v1/priorities", json=sample_priority_data.model_dump()
        )
        assert create_response.status == 201
        created_priority = await create_response.json()
        priority_key = created_priority["key"]
        invalid_data = PriorityPatch(
            name="This is a long name that is greater than 100 characters for this it must be more than 100 characters so we type a very long string so it will fail",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
        )
        response = await auth_client.patch(
            f"/api/v1/priority/{priority_key}", json=invalid_data.model_dump()
        )
        assert response.status == 422  # Validation error
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Name must be less than 100 characters"

    @pytest.mark.asyncio
    async def test_patch_priority_invalid_color(self, auth_client):
        """Test patching a priority with invalid data"""
        sample_priority_data = PriorityCreate(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
        )
        # First create a priority
        create_response = await auth_client.post(
            "/api/v1/priorities", json=sample_priority_data.model_dump()
        )
        assert create_response.status == 201
        created_priority = await create_response.json()
        priority_key = created_priority["key"]
        invalid_data = PriorityPatch(
            name="High",
            color="#00FM",
            icon="fa-chevron-up",
            order=1,
        )
        response = await auth_client.patch(
            f"/api/v1/priority/{priority_key}", json=invalid_data.model_dump()
        )
        assert response.status == 422  # Validation error
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Color must be a valid hex color"

    @pytest.mark.asyncio
    async def test_patch_priority_invalid_color_length(self, auth_client):
        """Test patching a priority with invalid data"""
        sample_priority_data = PriorityCreate(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
        )
        # First create a priority
        create_response = await auth_client.post(
            "/api/v1/priorities", json=sample_priority_data.model_dump()
        )
        assert create_response.status == 201
        created_priority = await create_response.json()
        priority_key = created_priority["key"]
        invalid_data = PriorityPatch(
            name="High",
            color="#0000000",
            icon="fa-chevron-up",
            order=1,
        )
        response = await auth_client.patch(
            f"/api/v1/priority/{priority_key}", json=invalid_data.model_dump()
        )
        assert response.status == 422  # Validation error
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Color must be less than 7 characters long"

    @pytest.mark.asyncio
    async def test_patch_priority_invalid_color_value(self, auth_client):
        """Test patching a priority with invalid data"""
        sample_priority_data = PriorityCreate(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
        )
        # First create a priority
        create_response = await auth_client.post(
            "/api/v1/priorities", json=sample_priority_data.model_dump()
        )
        assert create_response.status == 201
        created_priority = await create_response.json()
        priority_key = created_priority["key"]
        invalid_data = PriorityPatch(
            name="High",
            color="TESTING",
            icon="fa-chevron-up",
            order=1,
        )
        response = await auth_client.patch(
            f"/api/v1/priority/{priority_key}", json=invalid_data.model_dump()
        )
        assert response.status == 422  # Validation error
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Color must start with #"

    @pytest.mark.asyncio
    async def test_patch_priority_invalid_icon(self, auth_client):
        """Test patching a priority with invalid data"""
        sample_priority_data = PriorityCreate(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
        )
        # First create a priority
        create_response = await auth_client.post(
            "/api/v1/priorities", json=sample_priority_data.model_dump()
        )
        assert create_response.status == 201
        created_priority = await create_response.json()
        priority_key = created_priority["key"]
        invalid_data = PriorityPatch(
            name="High",
            color="#FF0000",
            icon=" ",
            order=1,
        )
        response = await auth_client.patch(
            f"/api/v1/priority/{priority_key}", json=invalid_data.model_dump()
        )
        assert response.status == 422  # Validation error
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Icon is required"

    @pytest.mark.asyncio
    async def test_patch_priority_invalid_order(self, auth_client):
        """Test patching a priority with invalid data"""
        sample_priority_data = PriorityCreate(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
        )
        # First create a priority
        create_response = await auth_client.post(
            "/api/v1/priorities", json=sample_priority_data.model_dump()
        )
        assert create_response.status == 201
        created_priority = await create_response.json()
        priority_key = created_priority["key"]
        invalid_data = PriorityPatch(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=0,
        )
        response = await auth_client.patch(
            f"/api/v1/priority/{priority_key}", json=invalid_data.model_dump()
        )
        assert response.status == 422  # Validation error
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Order must be greater than 0"


class TestDeletePriority:
    @pytest.mark.asyncio
    async def test_delete_priority_success(self, auth_client):
        """Test deleting a priority successfully"""
        sample_priority_data = PriorityCreate(
            name="High",
            color="#FF0000",
            icon="fa-chevron-up",
            order=1,
            user_key=auth_client.session.headers["User-Key"],
        )
        # First create a priority
        create_response = await auth_client.post(
            "/api/v1/priorities", json=sample_priority_data.model_dump()
        )
        assert create_response.status == 201
        created_priority = await create_response.json()
        priority_key = created_priority["key"]

        # Then delete the priority
        response = await auth_client.delete(f"/api/v1/priority/{priority_key}")
        assert response.status == 204

        # Verify the priority is deleted
        get_response = await auth_client.get(f"/api/v1/priority/{priority_key}")
        assert get_response.status == 404

    @pytest.mark.asyncio
    async def test_delete_priority_not_found(self, auth_client):
        """Test deleting a non-existent priority"""
        response = await auth_client.delete("/api/v1/priority/non-existent-key")
        assert response.status == 404
        data = await response.json()
        assert data["error"]["code"] == "not_found"
        assert (
            data["error"]["message"] == "Priority with key non-existent-key not found"
        )


class TestGetPrioritiesWithData:
    @pytest.mark.asyncio
    async def test_get_priorities_with_data(self, auth_client):
        """Test getting priorities when there is data in the database"""
        # Create multiple priorities
        for i in range(3):
            priority_data = PriorityCreate(
                name=f"Priority {i+1}",
                color="#FF0000",
                icon="fa-chevron-up",
                order=i + 1,
                user_key=auth_client.session.headers["User-Key"],
            )
            response = await auth_client.post(
                "/api/v1/priorities", json=priority_data.model_dump()
            )
            assert response.status == 201

        # Get all priorities
        response = await auth_client.get("/api/v1/priorities")
        assert response.status == 200
        data = await response.json()
        assert len(data["priorities"]) == 3
        assert data["total"] == 3
        assert data["success"] is True
