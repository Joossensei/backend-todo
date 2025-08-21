import pytest
from tests.factories import TodoFactory, PriorityFactory, StatusFactory
from app.schemas.todo import TodoCreate, TodoPatch, TodoUpdate


class TestGetTodos:
    """Test cases for todos API endpoints"""

    @pytest.mark.asyncio
    async def test_get_todos_with_data(self, auth_client, db_conn):
        user_key = auth_client.session.headers["User-Key"]
        # Create priorities for the user
        high_priority = await PriorityFactory.create_priority(
            db_conn, user_key, name="High", order=1
        )
        low_priority = await PriorityFactory.create_priority(
            db_conn, user_key, name="Low", order=3
        )

        # Create statuses for the user
        status_1 = await StatusFactory.create_status(
            db_conn, user_key, name="Status 1", order=1
        )
        status_2 = await StatusFactory.create_status(
            db_conn, user_key, name="Status 2", order=2
        )

        # Create todos
        await TodoFactory.create_todo(
            db_conn,
            user_key,
            high_priority["key"],
            status_1["key"],
            title="Important task",
        )
        await TodoFactory.create_todo(
            db_conn,
            user_key,
            low_priority["key"],
            status_2["key"],
            title="Less important",
        )

        # Test the endpoint
        resp = await auth_client.get("/api/v1/todos")
        assert resp.status == 200
        data = await resp.json()
        assert len(data["todos"]) == 2

    @pytest.mark.asyncio
    async def test_get_todos_empty(self, auth_client):
        """Test getting todos when database is empty"""
        response = await auth_client.get("/api/v1/todos")
        assert response.status == 200
        data = await response.json()
        assert "todos" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert "success" in data
        assert data["todos"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["size"] == 0
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_get_todos_with_pagination(self, auth_client):
        """Test getting todos with pagination parameters"""
        response = await auth_client.get("/api/v1/todos?page=2&size=5")
        assert response.status == 200
        data = await response.json()
        assert data["page"] == 2
        assert data["size"] == 0  # No todos in database


class TestCreateTodo:
    @pytest.mark.asyncio
    async def test_create_todo_success(self, auth_client, db_conn):
        user_key = auth_client.session.headers["User-Key"]
        priority = await PriorityFactory.create_priority(
            db_conn, user_key, name="High", order=1
        )
        status = await StatusFactory.create_status(
            db_conn, user_key, name="Status 1", order=1
        )
        """Test creating a todo successfully"""
        todo_data = TodoCreate(
            title="Test Todo",
            description="Test Description",
            priority=priority["key"],
            completed=False,
            user_key=user_key,
            status=status["key"],
        )
        response = await auth_client.post("/api/v1/todos", json=todo_data.model_dump())
        assert response.status == 201
        data = await response.json()
        assert "key" in data
        assert "title" in data
        assert "description" in data
        assert "priority" in data
        assert "completed" in data
        assert "created_at" in data
        assert data["title"] == todo_data.title
        assert data["description"] == todo_data.description
        assert data["priority"] == todo_data.priority
        assert data["completed"] == todo_data.completed
        assert data["status"] == todo_data.status


class TestCreateValidateTodo:
    @pytest.mark.asyncio
    async def test_create_todo_empty_title(self, auth_client, db_conn):
        """Test creating a todo with invalid data"""
        user_key = auth_client.session.headers["User-Key"]
        priority = await PriorityFactory.create_priority(
            db_conn, user_key, name="High", order=1
        )
        status = await StatusFactory.create_status(
            db_conn, user_key, name="Status 1", order=1
        )
        invalid_data = {
            "title": "",  # Empty title
            "description": "Test Description",
            "priority": priority["key"],
            "completed": False,
            "user_key": user_key,
            "status": status["key"],
        }
        response = await auth_client.post("/api/v1/todos", json=invalid_data)
        assert response.status == 422
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Title is required"

    @pytest.mark.asyncio
    async def test_create_todo_invalid_title_length(self, auth_client, db_conn):
        """Test creating a todo with invalid title length"""
        user_key = auth_client.session.headers["User-Key"]
        priority = await PriorityFactory.create_priority(
            db_conn, user_key, name="High", order=1
        )
        status = await StatusFactory.create_status(
            db_conn, user_key, name="Status 1", order=1
        )
        invalid_data = {
            "title": "A" * 101,  # Invalid title length
            "description": "Test Description",
            "priority": priority["key"],
            "completed": False,
            "user_key": user_key,
            "status": status["key"],
        }
        response = await auth_client.post("/api/v1/todos", json=invalid_data)
        assert response.status == 422
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Title must be less than 100 characters"

    @pytest.mark.asyncio
    async def test_create_todo_missing_required_fields(self, auth_client, db_conn):
        """Test creating a todo with missing required fields"""
        user_key = auth_client.session.headers["User-Key"]
        status = await StatusFactory.create_status(db_conn, user_key, name="Status 1")
        invalid_data = {
            "description": "Test Description",
            "completed": False,
            "status": status["key"],
        }
        response = await auth_client.post("/api/v1/todos", json=invalid_data)
        assert response.status == 422  # Validation error
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "All fields are required"

    @pytest.mark.asyncio
    async def test_create_todo_invalid_priority(self, auth_client, db_conn):
        """Test creating a todo with invalid priority"""
        user_key = auth_client.session.headers["User-Key"]
        status = await StatusFactory.create_status(db_conn, user_key, name="Status 1")
        invalid_data = {
            "title": "Test Todo",
            "priority": "invalid",
            "completed": False,
            "user_key": user_key,
            "status": status["key"],
        }
        response = await auth_client.post("/api/v1/todos", json=invalid_data)
        assert response.status == 422
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Priority not found"

    @pytest.mark.asyncio
    async def test_create_todo_invalid_completed(self, auth_client, db_conn):
        """Test creating a todo with invalid completed"""
        user_key = auth_client.session.headers["User-Key"]
        priority = await PriorityFactory.create_priority(
            db_conn, user_key, name="High", order=1
        )
        status = await StatusFactory.create_status(db_conn, user_key, name="Status 1")
        invalid_data = {
            "title": "Test Todo",
            "priority": priority["key"],
            "completed": None,
            "user_key": user_key,
            "status": status["key"],
        }
        response = await auth_client.post("/api/v1/todos", json=invalid_data)
        assert response.status == 422
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Completed is required"


class TestGetTodoByKey:
    @pytest.mark.asyncio
    async def test_get_todo_by_key_success(self, auth_client, db_conn):
        """Test getting a todo by key successfully"""
        user_key = auth_client.session.headers["User-Key"]
        priority = await PriorityFactory.create_priority(
            db_conn, user_key, name="High", order=1
        )
        status = await StatusFactory.create_status(
            db_conn, user_key, name="Status 1", order=1
        )
        todo_data = TodoCreate(
            title="Test Todo",
            description="Test Description",
            priority=priority["key"],
            completed=False,
            user_key=user_key,
            status=status["key"],
        )
        create_response = await auth_client.post(
            "/api/v1/todos", json=todo_data.model_dump()
        )
        assert create_response.status == 201
        created_todo = await create_response.json()
        todo_key = created_todo["key"]

        response = await auth_client.get(f"/api/v1/todo/{todo_key}")
        assert response.status == 200
        data = await response.json()
        assert data["key"] == todo_key
        assert data["title"] == todo_data.title

    @pytest.mark.asyncio
    async def test_get_todo_by_key_not_found(self, auth_client):
        """Test getting a todo by non-existent key"""
        response = await auth_client.get("/api/v1/todo/non-existent-key")
        assert response.status == 404
        data = await response.json()
        assert "error" in data
        assert "code" in data["error"]
        assert data["error"]["code"] == "not_found"
        assert data["error"]["message"] == "Todo with key non-existent-key not found"


class TestUpdateTodo:
    @pytest.mark.asyncio
    async def test_update_todo_success(
        self,
        auth_client,
        db_conn,
    ):
        """Test updating a todo successfully"""
        user_key = auth_client.session.headers["User-Key"]
        priority = await PriorityFactory.create_priority(
            db_conn, user_key, name="High", order=1
        )
        status = await StatusFactory.create_status(
            db_conn, user_key, name="Status 1", order=1
        )
        todo_data = TodoCreate(
            title="Test Todo",
            description="Test Description",
            priority=priority["key"],
            completed=False,
            user_key=user_key,
            status=status["key"],
        )
        todo_update_data = TodoUpdate(
            title="Updated Todo",
            description="Updated Description",
            priority=priority["key"],
            completed=True,
            status=status["key"],
        )
        create_response = await auth_client.post(
            "/api/v1/todos", json=todo_data.model_dump()
        )
        assert create_response.status == 201
        created_todo = await create_response.json()
        todo_key = created_todo["key"]

        # Then update the todo
        response = await auth_client.put(
            f"/api/v1/todo/{todo_key}", json=todo_update_data.model_dump()
        )
        assert response.status == 200
        data = await response.json()
        assert data["title"] == todo_update_data.title
        assert data["description"] == todo_update_data.description
        assert data["priority"] == todo_update_data.priority
        assert data["completed"] == todo_update_data.completed
        assert data["status"] == todo_update_data.status

    @pytest.mark.asyncio
    async def test_update_todo_not_found(self, auth_client, db_conn):
        """Test updating a non-existent todo"""
        user_key = auth_client.session.headers["User-Key"]
        priority = await PriorityFactory.create_priority(
            db_conn, user_key, name="High", order=1
        )
        status = await StatusFactory.create_status(
            db_conn, user_key, name="Status 1", order=1
        )
        todo_update_data = TodoUpdate(
            title="Updated Todo",
            description="Updated Description",
            priority=priority["key"],
            completed=True,
            status=status["key"],
        )
        response = await auth_client.put(
            "/api/v1/todo/non-existent-key", json=todo_update_data.model_dump()
        )
        assert response.status == 404
        data = await response.json()
        assert "error" in data
        assert data["error"]["code"] == "not_found"
        assert data["error"]["message"] == "Todo with key non-existent-key not found"


class TestUpdateValidateTodo:
    @pytest.mark.asyncio
    async def test_update_todo_invalid_priority(self, auth_client, db_conn):
        """Test updating a todo with invalid priority"""
        user_key = auth_client.session.headers["User-Key"]
        priority = await PriorityFactory.create_priority(
            db_conn, user_key, name="High", order=1
        )
        status = await StatusFactory.create_status(
            db_conn, user_key, name="Status 1", order=1
        )
        # Create a todo
        todo_data = TodoCreate(
            title="Test Todo",
            description="Test Description",
            priority=priority["key"],
            completed=False,
            user_key=user_key,
            status=status["key"],
        )
        create_response = await auth_client.post(
            "/api/v1/todos", json=todo_data.model_dump()
        )
        assert create_response.status == 201
        created_todo = await create_response.json()
        todo_key = created_todo["key"]

        # Then update the todo
        invalid_data = {
            "title": "Test Todo",
            "description": "Test Description",
            "priority": "invalid",
            "completed": False,
            "status": status["key"],
        }
        response = await auth_client.put(f"/api/v1/todo/{todo_key}", json=invalid_data)
        assert response.status == 422
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Priority not found"

    @pytest.mark.asyncio
    async def test_update_todo_invalid_title(self, auth_client, db_conn):
        """Test updating a todo with invalid title"""
        user_key = auth_client.session.headers["User-Key"]
        priority = await PriorityFactory.create_priority(
            db_conn, user_key, name="High", order=1
        )
        status = await StatusFactory.create_status(
            db_conn, user_key, name="Status 1", order=1
        )
        todo_data = TodoCreate(
            title="Test Todo",
            description="Test Description",
            priority=priority["key"],
            completed=False,
            user_key=user_key,
            status=status["key"],
        )
        create_response = await auth_client.post(
            "/api/v1/todos", json=todo_data.model_dump()
        )
        assert create_response.status == 201
        created_todo = await create_response.json()
        todo_key = created_todo["key"]

        # Then update the todo
        invalid_data = {
            "title": "A" * 101,
            "description": "Test Description",
            "priority": priority["key"],
            "completed": False,
            "user_key": user_key,
            "status": status["key"],
        }
        response = await auth_client.put(f"/api/v1/todo/{todo_key}", json=invalid_data)
        assert response.status == 422
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Title must be less than 100 characters"

    @pytest.mark.asyncio
    async def test_update_todo_invalid_description(self, auth_client, db_conn):
        """Test updating a todo with invalid description"""
        user_key = auth_client.session.headers["User-Key"]
        priority = await PriorityFactory.create_priority(
            db_conn, user_key, name="High", order=1
        )
        status = await StatusFactory.create_status(
            db_conn, user_key, name="Status 1", order=1
        )
        todo_data = TodoCreate(
            title="Test Todo",
            description="Test Description",
            priority=priority["key"],
            completed=False,
            user_key=user_key,
            status=status["key"],
        )
        create_response = await auth_client.post(
            "/api/v1/todos", json=todo_data.model_dump()
        )
        assert create_response.status == 201
        created_todo = await create_response.json()
        todo_key = created_todo["key"]

        # Then update the todo
        invalid_data = {
            "title": "Test Todo",
            "description": "A" * 1001,
            "priority": priority["key"],
            "completed": False,
            "user_key": user_key,
            "status": status["key"],
        }
        response = await auth_client.put(f"/api/v1/todo/{todo_key}", json=invalid_data)
        assert response.status == 422
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert (
            data["error"]["message"] == "Description must be less than 1000 characters"
        )


class TestPatchTodo:
    @pytest.mark.asyncio
    async def test_patch_todo_success(self, auth_client, db_conn):
        """Test patching a todo successfully"""
        user_key = auth_client.session.headers["User-Key"]
        priority = await PriorityFactory.create_priority(
            db_conn, user_key, name="High", order=1
        )
        status = await StatusFactory.create_status(
            db_conn, user_key, name="Status 1", order=1
        )
        todo_data = TodoCreate(
            title="Test Todo",
            description="Test Description",
            priority=priority["key"],
            completed=False,
            user_key=user_key,
            status=status["key"],
        )
        create_response = await auth_client.post(
            "/api/v1/todos", json=todo_data.model_dump()
        )
        assert create_response.status == 201
        created_todo = await create_response.json()
        todo_key = created_todo["key"]

        # Then patch the todo
        patch_data = TodoPatch(
            title="Patched Title",
            completed=True,
            status=status["key"],
        )
        response = await auth_client.patch(
            f"/api/v1/todo/{todo_key}", json=patch_data.model_dump()
        )
        assert response.status == 200
        data = await response.json()
        assert data["title"] == "Patched Title"
        assert data["completed"] is True
        assert data["description"] == todo_data.description
        assert data["priority"] == todo_data.priority
        assert data["status"] == todo_data.status

    @pytest.mark.asyncio
    async def test_patch_todo_not_found(self, auth_client):
        """Test patching a non-existent todo"""
        patch_data = TodoPatch(
            title="Patched Title",
            completed=True,
        )
        response = await auth_client.patch(
            "/api/v1/todo/non-existent-key", json=patch_data.model_dump()
        )
        assert response.status == 404
        data = await response.json()
        assert "error" in data
        assert data["error"]["code"] == "not_found"
        assert data["error"]["message"] == "Todo with key non-existent-key not found"


class TestPatchValidateTodo:
    @pytest.mark.asyncio
    async def test_patch_todo_invalid_title(self, auth_client, db_conn):
        """Test patching a todo with invalid title"""
        user_key = auth_client.session.headers["User-Key"]
        priority = await PriorityFactory.create_priority(
            db_conn, user_key, name="High", order=1
        )
        status = await StatusFactory.create_status(
            db_conn, user_key, name="Status 1", order=1
        )
        todo_data = TodoCreate(
            title="Test Todo",
            description="Test Description",
            priority=priority["key"],
            completed=False,
            user_key=user_key,
            status=status["key"],
        )
        create_response = await auth_client.post(
            "/api/v1/todos", json=todo_data.model_dump()
        )
        assert create_response.status == 201
        created_todo = await create_response.json()
        todo_key = created_todo["key"]

        # Then patch the todo
        invalid_data = {
            "title": "A" * 101,
            "completed": True,
            "status": status["key"],
        }
        response = await auth_client.patch(
            f"/api/v1/todo/{todo_key}", json=invalid_data
        )
        assert response.status == 422
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Title must be less than 100 characters"

    @pytest.mark.asyncio
    async def test_patch_todo_invalid_priority(self, auth_client, db_conn):
        """Test patching a todo with invalid priority"""
        user_key = auth_client.session.headers["User-Key"]
        priority = await PriorityFactory.create_priority(
            db_conn, user_key, name="High", order=1
        )
        status = await StatusFactory.create_status(
            db_conn, user_key, name="Status 1", order=1
        )
        todo_data = TodoCreate(
            title="Test Todo",
            description="Test Description",
            priority=priority["key"],
            completed=False,
            user_key=user_key,
            status=status["key"],
        )
        create_response = await auth_client.post(
            "/api/v1/todos", json=todo_data.model_dump()
        )
        assert create_response.status == 201
        created_todo = await create_response.json()
        todo_key = created_todo["key"]

        # Then patch the todo
        invalid_data = {
            "title": "Test Todo",
            "description": "Test Description",
            "priority": "invalid",
            "completed": False,
            "status": status["key"],
        }
        response = await auth_client.patch(
            f"/api/v1/todo/{todo_key}", json=invalid_data
        )
        assert response.status == 422
        data = await response.json()
        assert data["error"]["code"] == "validation_error"
        assert data["error"]["message"] == "Priority not found"


class TestDeleteTodo:
    @pytest.mark.asyncio
    async def test_delete_todo_success(self, auth_client, db_conn):
        """Test deleting a todo successfully"""
        user_key = auth_client.session.headers["User-Key"]
        priority = await PriorityFactory.create_priority(
            db_conn, user_key, name="High", order=1
        )
        status = await StatusFactory.create_status(
            db_conn, user_key, name="Status 1", order=1
        )
        todo_data = TodoCreate(
            title="Test Todo",
            description="Test Description",
            priority=priority["key"],
            completed=False,
            user_key=user_key,
            status=status["key"],
        )
        create_response = await auth_client.post(
            "/api/v1/todos", json=todo_data.model_dump()
        )
        assert create_response.status == 201
        created_todo = await create_response.json()
        todo_key = created_todo["key"]

        # Then delete the todo
        response = await auth_client.delete(f"/api/v1/todo/{todo_key}")
        assert response.status == 204

        # Verify the todo is deleted
        get_response = await auth_client.get(f"/api/v1/todo/{todo_key}")
        assert get_response.status == 404
        data = await get_response.json()
        assert "error" in data
        assert data["error"]["code"] == "not_found"
        assert data["error"]["message"] == f"Todo with key {todo_key} not found"

    @pytest.mark.asyncio
    async def test_delete_todo_not_found(self, auth_client):
        """Test deleting a non-existent todo"""
        response = await auth_client.delete("/api/v1/todo/non-existent-key")
        assert response.status == 404
        data = await response.json()
        assert "error" in data
        assert data["error"]["code"] == "not_found"
        assert data["error"]["message"] == "Todo with key non-existent-key not found"
