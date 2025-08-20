import pytest
import logging
from tests.factories import UserFactory
from app.schemas.user import UserCreate, UserUpdate, UserUpdatePassword

logger = logging.getLogger(__name__)


class TestGetUsers:

    @pytest.mark.asyncio
    async def test_get_users_no_data(self, auth_client):
        """Test getting users when database is empty"""
        response = await auth_client.get("/api/v1/users")
        assert response.status == 200
        data = await response.json()
        assert "users" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert "success" in data
        assert len(data["users"]) == 1
        assert data["total"] == 1
        assert data["page"] == 1
        assert data["size"] == 1
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_get_users_with_pagination(self, auth_client, db_conn):
        """Test getting users with pagination parameters"""
        await UserFactory.create_user(db_conn)
        await UserFactory.create_user(db_conn)
        response = await auth_client.get("/api/v1/users?page=2&size=2")
        assert response.status == 200
        data = await response.json()
        assert data["page"] == 2
        assert data["size"] == 1  # Should have 1 user on page 2

    @pytest.mark.asyncio
    async def test_get_users_with_pagination_no_data(self, auth_client):
        """Test getting users with pagination parameters when no data"""
        response = await auth_client.get("/api/v1/users?page=2&size=5")
        assert response.status == 200
        data = await response.json()
        assert data["page"] == 2
        assert data["size"] == 0  # No users in database

    @pytest.mark.asyncio
    async def test_get_users_no_auth(self, client):
        """Test getting users without authentication"""
        response = await client.get("/api/v1/users")
        assert response.status == 401
        data = await response.json()
        assert data["detail"] == "Missing or invalid token"


class TestCreateUser:
    @pytest.mark.asyncio
    async def test_create_user_success(self, auth_client):
        """Test creating a user successfully"""
        sample_user_data = UserCreate(
            name="Test User",
            username="testuser1",
            email="test@example.com",
            password="Securepassword123",
            is_active=True,
        )
        response = await auth_client.post(
            "/api/v1/users", json=sample_user_data.model_dump()
        )
        assert response.status == 201
        data = await response.json()
        assert "key" in data
        assert "name" in data
        assert "username" in data
        assert "email" in data
        assert "is_active" in data
        assert "created_at" in data
        assert data["name"] == sample_user_data.name
        assert data["username"] == sample_user_data.username
        assert data["email"] == sample_user_data.email
        assert data["is_active"] == sample_user_data.is_active
        # Password should not be returned
        assert "password" not in data
        assert "hashed_password" not in data


class TestCreateValidateUser:
    @pytest.mark.asyncio
    async def test_create_user_empty_name(self, auth_client):
        """Test creating a user with empty name"""
        invalid_data = {
            "name": "",
            "username": "testuser",
            "email": "test@example.com",
            "password": "Securepassword123",
            "is_active": True,
        }
        response = await auth_client.post("/api/v1/users", json=invalid_data)
        assert response.status == 422
        data = await response.json()
        assert data["error"]["code"] == "validation_error"

    @pytest.mark.asyncio
    async def test_create_user_empty_username(self, auth_client):
        """Test creating a user with empty username"""
        invalid_data = {
            "name": "Test User",
            "username": "",
            "email": "test@example.com",
            "password": "Securepassword123",
            "is_active": True,
        }
        response = await auth_client.post("/api/v1/users", json=invalid_data)
        assert response.status == 422
        data = await response.json()
        assert data["error"]["code"] == "validation_error"

    @pytest.mark.asyncio
    async def test_create_user_invalid_email(self, auth_client):
        """Test creating a user with invalid email"""
        invalid_data = {
            "name": "Test User",
            "username": "testuser",
            "email": "invalid-email",
            "password": "Securepassword123",
            "is_active": True,
        }
        response = await auth_client.post("/api/v1/users", json=invalid_data)
        assert response.status == 422
        data = await response.json()
        assert data["error"]["code"] == "validation_error"

    @pytest.mark.asyncio
    async def test_create_user_empty_password(self, auth_client):
        """Test creating a user with empty password"""
        invalid_data = {
            "name": "Test User",
            "username": "testuser",
            "email": "test@example.com",
            "password": "",
            "is_active": True,
        }
        response = await auth_client.post("/api/v1/users", json=invalid_data)
        assert response.status == 422
        data = await response.json()
        assert data["error"]["code"] == "validation_error"

    @pytest.mark.asyncio
    async def test_create_user_duplicate_username(self, auth_client, db_conn):
        """Test creating a user with duplicate username"""
        # First create a user
        user1_data = UserCreate(
            name="Test User 1",
            username="testuser1",
            email="test1@example.com",
            password="Securepassword123",
            is_active=True,
        )
        response1 = await auth_client.post(
            "/api/v1/users", json=user1_data.model_dump()
        )
        assert response1.status == 201

        # Try to create another user with same username
        user2_data = UserCreate(
            name="Test User 2",
            username="testuser1",  # Same username
            email="test2@example.com",
            password="Securepassword123",
            is_active=True,
        )
        response2 = await auth_client.post(
            "/api/v1/users", json=user2_data.model_dump()
        )
        assert response2.status == 422
        data = await response2.json()
        assert data["error"]["code"] == "validation_error"
        assert "Username already exists" in data["error"]["message"]

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, auth_client, db_conn):
        """Test creating a user with duplicate email"""
        # First create a user
        user1_data = UserCreate(
            name="Test User 1",
            username="testuser1",
            email="test@example.com",
            password="Securepassword123",
            is_active=True,
        )
        response1 = await auth_client.post(
            "/api/v1/users", json=user1_data.model_dump()
        )
        assert response1.status == 201

        # Try to create another user with same email
        user2_data = UserCreate(
            name="Test User 2",
            username="testuser2",
            email="test@example.com",  # Same email
            password="Securepassword123",
            is_active=True,
        )
        response2 = await auth_client.post(
            "/api/v1/users", json=user2_data.model_dump()
        )
        assert response2.status == 422
        data = await response2.json()
        assert data["error"]["code"] == "validation_error"
        assert "email" in data["error"]["message"].lower()

    @pytest.mark.asyncio
    async def test_create_user_missing_required_fields(self, auth_client):
        """Test creating a user with missing required fields"""
        invalid_data = {"name": "Test User", "email": "test@example.com"}
        response = await auth_client.post("/api/v1/users", json=invalid_data)
        assert response.status == 422
        data = await response.json()
        logger.error(data)
        assert data["error"]["code"] == "validation_error"


class TestGetUserByKey:
    @pytest.mark.asyncio
    async def test_get_user_by_key_success(self, auth_client, db_conn):
        """Test getting a user by key successfully"""
        # First create a user
        user_data = UserCreate(
            name="Test User",
            username="testuser",
            email="test@example.com",
            password="Securepassword123",
            is_active=True,
        )
        create_response = await auth_client.post(
            "/api/v1/users", json=user_data.model_dump()
        )
        assert create_response.status == 201
        created_user = await create_response.json()
        user_key = created_user["key"]

        # Then get the user by key
        response = await auth_client.get(f"/api/v1/user/{user_key}")
        assert response.status == 200
        data = await response.json()
        assert data["key"] == user_key
        assert data["name"] == user_data.name
        assert data["username"] == user_data.username
        assert data["email"] == user_data.email
        assert data["is_active"] == user_data.is_active

    @pytest.mark.asyncio
    async def test_get_user_by_key_not_found(self, auth_client):
        """Test getting a user by non-existent key"""
        response = await auth_client.get("/api/v1/user/non-existent-key")
        assert response.status == 404
        data = await response.json()
        assert data["error"]["code"] == "not_found"
        assert data["error"]["message"] == "User with key non-existent-key not found"


class TestUpdateUser:
    @pytest.mark.asyncio
    async def test_update_user_success(self, auth_client, db_conn):
        """Test updating a user successfully"""
        # Use our own user as we can't update other users
        user_key = auth_client.session.headers["User-Key"]
        user_data = await auth_client.get(f"/api/v1/user/{user_key}")
        user_data = await user_data.json()

        # Update the user
        update_data = UserUpdate(
            name="Very Authenticated User",
            email="very.authenticated@example.com",
            is_active=False,
        )
        response = await auth_client.put(
            f"/api/v1/user/{user_key}", json=update_data.model_dump()
        )
        assert response.status == 200
        data = await response.json()
        assert data["name"] == update_data.name
        assert data["email"] == update_data.email
        assert data["is_active"] == update_data.is_active
        # Username should remain unchanged
        assert data["username"] == user_data["username"]

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, auth_client):
        """Test updating a non-existent user"""
        update_data = UserUpdate(
            name="Updated User",
            email="updated@example.com",
            is_active=False,
        )
        response = await auth_client.put(
            "/api/v1/user/non-existent-key", json=update_data.model_dump()
        )
        assert response.status == 404
        data = await response.json()
        logger.error(data)
        assert data["error"]["code"] == "not_found"
        assert data["error"]["message"] == "User with key non-existent-key not found"

    @pytest.mark.asyncio
    async def test_update_user_unauthorized(self, client, db_conn):
        """Test updating a user that is not the current user"""
        # Try to update user2 while authenticated as user1
        user2 = await UserFactory.create_user(db_conn)
        update_data = UserUpdate(name="Hacked User")
        response = await client.put(
            f"/api/v1/user/{user2['key']}", json=update_data.model_dump()
        )
        assert response.status == 401
        data = await response.json()
        assert data["detail"] == "Missing or invalid token"


class TestUpdateValidateUser:
    @pytest.mark.asyncio
    async def test_update_user_invalid_email(self, auth_client, db_conn):
        """Test updating a user with invalid email"""
        # First create a user
        user_data = UserCreate(
            name="Test User",
            username="testuser",
            email="test@example.com",
            password="Securepassword123",
            is_active=True,
        )
        create_response = await auth_client.post(
            "/api/v1/users", json=user_data.model_dump()
        )
        assert create_response.status == 201
        created_user = await create_response.json()
        user_key = created_user["key"]

        # Try to update with invalid email
        invalid_data = {
            "name": "Test User",
            "email": "invalid-email",
            "is_active": True,
        }
        response = await auth_client.put(f"/api/v1/user/{user_key}", json=invalid_data)
        assert response.status == 422
        data = await response.json()
        assert data["error"]["code"] == "validation_error"

    @pytest.mark.asyncio
    async def test_update_user_empty_name(self, auth_client, db_conn):
        """Test updating a user with empty name"""
        # First create a user
        user_data = UserCreate(
            name="Test User",
            username="testuser",
            email="test@example.com",
            password="Securepassword123",
            is_active=True,
        )
        create_response = await auth_client.post(
            "/api/v1/users", json=user_data.model_dump()
        )
        assert create_response.status == 201
        created_user = await create_response.json()
        user_key = created_user["key"]

        # Try to update with empty name
        invalid_data = {
            "name": "",
            "email": "test@example.com",
            "is_active": True,
        }
        response = await auth_client.put(f"/api/v1/user/{user_key}", json=invalid_data)
        assert response.status == 422
        data = await response.json()
        assert data["error"]["code"] == "validation_error"


class TestUpdateUserPassword:
    @pytest.mark.asyncio
    async def test_update_user_password_success(self, auth_client, db_conn):
        """Test updating a user password successfully"""
        user_key = auth_client.session.headers["User-Key"]

        # Update the password
        password_data = UserUpdatePassword(
            current_password="Test123",
            password="Newpassword123",
        )
        response = await auth_client.put(
            f"/api/v1/user/{user_key}/password", json=password_data.model_dump()
        )
        assert response.status == 200
        data = await response.json()
        assert data["message"] == "User password updated successfully"
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_update_user_password_wrong_current_password(
        self, auth_client, db_conn
    ):
        """Test updating password with wrong current password"""
        user_key = auth_client.session.headers["User-Key"]

        # Try to update with wrong current password
        password_data = UserUpdatePassword(
            current_password="Wrongpassword123",
            password="Newpassword123",
        )
        response = await auth_client.put(
            f"/api/v1/user/{user_key}/password", json=password_data.model_dump()
        )
        assert response.status == 422
        data = await response.json()
        assert data["error"]["code"] == "validation_error"

    @pytest.mark.asyncio
    async def test_update_user_password_unauthorized(self, client, db_conn):
        """Test updating password for a user that is not the current user"""
        user2 = await UserFactory.create_user(db_conn)

        # Try to update user2's password while unauthenticated
        password_data = UserUpdatePassword(
            current_password="Test123",
            password="Newpassword123",
        )
        response = await client.put(
            f"/api/v1/user/{user2['key']}/password", json=password_data.model_dump()
        )
        assert response.status == 401
        data = await response.json()
        assert data["detail"] == "Missing or invalid token"

    @pytest.mark.asyncio
    async def test_update_user_password_empty_new_password(self, auth_client, db_conn):
        """Test updating password with empty new password"""
        user_key = auth_client.session.headers["User-Key"]

        # Try to update with empty new password
        password_data = {
            "current_password": "Test123",
            "password": "",
        }
        response = await auth_client.put(
            f"/api/v1/user/{user_key}/password", json=password_data
        )
        assert response.status == 422
        data = await response.json()
        assert data["error"]["code"] == "validation_error"


class TestDeleteUser:
    @pytest.mark.asyncio
    async def test_delete_user_success(self, auth_client, db_conn):
        """Test deleting a user successfully"""
        # Create a new authenticated user
        user_data = UserCreate(
            name="Test User",
            username="testuser",
            email="test@example.com",
            password="Securepassword123",
            is_active=True,
        )
        response = await auth_client.post("/api/v1/users", json=user_data.model_dump())
        assert response.status == 201
        created_user = await response.json()
        user_key = created_user["key"]

        # get a token for the new user
        token_response = await auth_client.post(
            "/api/v1/token",
            data={"username": "testuser", "password": "Securepassword123"},
        )
        assert token_response.status == 200
        token_data = await token_response.json()
        logger.error(token_data)
        token = token_data["access_token"]
        user_key = token_data["user_key"]

        # set the token in the headers
        old_token = auth_client.session.headers["Authorization"]
        auth_client.session.headers["Authorization"] = f"Bearer {token}"

        # Then delete the user
        response = await auth_client.delete(f"/api/v1/user/{user_key}")
        assert response.status == 204

        # Return to the old token
        auth_client.session.headers["Authorization"] = old_token
        # Verify the user is deleted
        get_response = await auth_client.get(f"/api/v1/user/{user_key}")
        assert get_response.status == 404

    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, auth_client):
        """Test deleting a non-existent user"""
        response = await auth_client.delete("/api/v1/user/non-existent-key")
        assert response.status == 404
        data = await response.json()
        assert data["error"]["code"] == "not_found"
        assert data["error"]["message"] == "User with key non-existent-key not found"

    @pytest.mark.asyncio
    async def test_delete_user_unauthorized(self, client, db_conn):
        """Test deleting a user that is not the current user"""
        # Create two users
        user1 = await UserFactory.create_user(db_conn)
        # Try to delete while not authenticated
        response = await client.delete(f"/api/v1/user/{user1['key']}")
        assert response.status == 401
        data = await response.json()
        assert data["detail"] == "Missing or invalid token"


class TestGetUsersWithData:
    @pytest.mark.asyncio
    async def test_get_users_with_data(self, auth_client, db_conn):
        """Test getting users when there is data in the database"""
        # Create multiple users
        for i in range(3):
            user_data = UserCreate(
                name=f"User {i+1}",
                username=f"user{i+1}",
                email=f"user{i+1}@example.com",
                password="Securepassword123",
                is_active=True,
            )
            response = await auth_client.post(
                "/api/v1/users", json=user_data.model_dump()
            )
            assert response.status == 201

        # Get all users
        response = await auth_client.get("/api/v1/users")
        assert response.status == 200
        data = await response.json()
        assert (
            len(data["users"]) >= 3
        )  # At least 3 users (including the authenticated user)
        assert data["total"] >= 3
        assert data["success"] is True
