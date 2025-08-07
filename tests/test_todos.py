from fastapi.testclient import TestClient


class TestTodosAPI:
    """Test cases for todos API endpoints"""

    def test_get_todos_empty(self, client: TestClient):
        """Test getting todos when database is empty"""
        response = client.get("/api/v1/todos/")
        assert response.status_code == 200
        data = response.json()
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

    def test_get_todos_with_pagination(self, client: TestClient):
        """Test getting todos with pagination parameters"""
        response = client.get("/api/v1/todos/?page=2&size=5")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert data["size"] == 0  # No todos in database

    def test_create_todo_success(
        self, client: TestClient, sample_todo_with_priority_data
    ):
        """Test creating a todo successfully"""
        response = client.post("/api/v1/todos/", json=sample_todo_with_priority_data)
        print(response.json())
        assert response.status_code == 200
        data = response.json()
        assert "key" in data
        assert "title" in data
        assert "description" in data
        assert "priority" in data
        assert "completed" in data
        assert "created_at" in data
        assert data["title"] == sample_todo_with_priority_data["title"]
        assert data["description"] == sample_todo_with_priority_data["description"]
        assert data["priority"] == sample_todo_with_priority_data["priority"]
        assert data["completed"] == sample_todo_with_priority_data["completed"]

    def test_create_todo_invalid_data(self, client: TestClient):
        """Test creating a todo with invalid data"""
        invalid_data = {
            "title": "",  # Empty title
            "description": "Test Description",
            "priority": "non-existent-priority-key",
            "completed": False,
        }
        response = client.post("/api/v1/todos/", json=invalid_data)
        assert response.status_code == 422  # Validation error for empty title

    def test_create_todo_missing_required_fields(self, client: TestClient):
        """Test creating a todo with missing required fields"""
        invalid_data = {"description": "Test Description", "completed": False}
        response = client.post("/api/v1/todos/", json=invalid_data)
        assert response.status_code == 422  # Validation error

    def test_get_todo_by_key_success(
        self, client: TestClient, sample_todo_with_priority_data
    ):
        """Test getting a todo by key successfully"""
        # First create a todo
        create_response = client.post(
            "/api/v1/todos/", json=sample_todo_with_priority_data
        )
        assert create_response.status_code == 200
        created_todo = create_response.json()
        todo_key = created_todo["key"]

        # Then get the todo by key
        response = client.get(f"/api/v1/todos/{todo_key}")
        assert response.status_code == 200
        data = response.json()
        assert data["key"] == todo_key
        assert data["title"] == sample_todo_with_priority_data["title"]

    def test_get_todo_by_key_not_found(self, client: TestClient):
        """Test getting a todo by non-existent key"""
        response = client.get("/api/v1/todos/non-existent-key")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"]

    def test_update_todo_success(
        self,
        client: TestClient,
        sample_todo_with_priority_data,
        sample_todo_update_data,
    ):
        """Test updating a todo successfully"""
        # First create a todo
        create_response = client.post(
            "/api/v1/todos/", json=sample_todo_with_priority_data
        )
        assert create_response.status_code == 200
        created_todo = create_response.json()
        todo_key = created_todo["key"]

        # Then update the todo
        response = client.put(f"/api/v1/todos/{todo_key}", json=sample_todo_update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == sample_todo_update_data["title"]
        assert data["description"] == sample_todo_update_data["description"]
        assert data["priority"] == sample_todo_update_data["priority"]
        assert data["completed"] == sample_todo_update_data["completed"]

    def test_update_todo_not_found(self, client: TestClient, sample_todo_update_data):
        """Test updating a non-existent todo"""
        response = client.put(
            "/api/v1/todos/non-existent-key", json=sample_todo_update_data
        )
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"]

    def test_patch_todo_success(
        self, client: TestClient, sample_todo_with_priority_data
    ):
        """Test patching a todo successfully"""
        # First create a todo
        create_response = client.post(
            "/api/v1/todos/", json=sample_todo_with_priority_data
        )
        assert create_response.status_code == 200
        created_todo = create_response.json()
        todo_key = created_todo["key"]

        # Then patch the todo
        patch_data = {"title": "Patched Title", "completed": True}
        response = client.patch(f"/api/v1/todos/{todo_key}", json=patch_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Patched Title"
        assert data["completed"] is True
        # Other fields should remain unchanged
        assert data["description"] == sample_todo_with_priority_data["description"]
        assert data["priority"] == sample_todo_with_priority_data["priority"]

    def test_patch_todo_not_found(self, client: TestClient):
        """Test patching a non-existent todo"""
        patch_data = {"title": "Patched Title"}
        response = client.patch("/api/v1/todos/non-existent-key", json=patch_data)
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"]

    def test_delete_todo_success(
        self, client: TestClient, sample_todo_with_priority_data
    ):
        """Test deleting a todo successfully"""
        # First create a todo
        create_response = client.post(
            "/api/v1/todos/", json=sample_todo_with_priority_data
        )
        assert create_response.status_code == 200
        created_todo = create_response.json()
        todo_key = created_todo["key"]

        # Then delete the todo
        response = client.delete(f"/api/v1/todos/{todo_key}")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "deleted successfully" in data["message"]

        # Verify the todo is deleted
        get_response = client.get(f"/api/v1/todos/{todo_key}")
        assert get_response.status_code == 404

    def test_delete_todo_not_found(self, client: TestClient):
        """Test deleting a non-existent todo"""
        response = client.delete("/api/v1/todos/non-existent-key")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"]

    def test_get_todos_with_data(self, client: TestClient, sample_priority_data):
        """Test getting todos when there is data in the database"""
        # Create multiple todos with different priorities
        for i in range(3):
            # Create a new priority for each todo
            priority_data = sample_priority_data.copy()
            priority_data["name"] = f"Priority {i+1}"
            priority_response = client.post("/api/v1/priorities/", json=priority_data)
            assert priority_response.status_code == 200
            priority_key = priority_response.json()["key"]

            # Create todo with this priority
            todo_data = {
                "title": f"Todo {i+1}",
                "description": "Test Description",
                "priority": priority_key,
                "completed": False,
            }
            response = client.post("/api/v1/todos/", json=todo_data)
            assert response.status_code == 200

        # Get all todos
        response = client.get("/api/v1/todos/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["todos"]) == 3
        assert data["total"] == 3
        assert data["success"] is True
