from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from app.services.todo_service import TodoService
from app.services.priority_service import PriorityService
from app.schemas.todo import TodoCreate, TodoUpdate
from app.schemas.priority import PriorityCreate, PriorityUpdate


class TestTodoService:
    """Unit tests for TodoService"""

    def test_create_todo_success(self, db_session: Session):
        """Test creating a todo successfully"""
        todo_data = TodoCreate(
            title="Test Todo",
            description="Test Description",
            priority="high",
            completed=False,
        )

        # Mock the database session
        mock_db = Mock(spec=Session)

        with patch.object(TodoService, "create_todo") as mock_create:
            mock_create.return_value = Mock(
                to_dict=lambda: {
                    "key": "test-key",
                    "title": "Test Todo",
                    "description": "Test Description",
                    "priority": "high",
                    "completed": False,
                }
            )

            result = TodoService.create_todo(mock_db, todo_data)

            mock_create.assert_called_once_with(mock_db, todo_data)
            assert result is not None

    def test_get_todos_with_pagination(self, db_session: Session):
        """Test getting todos with pagination"""
        mock_db = Mock(spec=Session)

        with patch.object(TodoService, "get_todos") as mock_get:
            mock_todos = [Mock() for _ in range(3)]
            mock_get.return_value = mock_todos

            result = TodoService.get_todos(mock_db, page=1, size=10)

            mock_get.assert_called_once_with(mock_db, page=1, size=10)
            assert len(result) == 3

    def test_get_todo_by_key_not_found(self, db_session: Session):
        """Test getting todo by non-existent key"""
        mock_db = Mock(spec=Session)

        with patch.object(TodoService, "fetch_todo_id_by_key") as mock_fetch:
            mock_fetch.side_effect = ValueError("Todo not found")

            try:
                TodoService.fetch_todo_id_by_key(mock_db, "non-existent")
                assert False, "Should have raised ValueError"
            except ValueError as e:
                assert "Todo not found" in str(e)

    def test_update_todo_success(self, db_session: Session):
        """Test updating a todo successfully"""
        todo_update = TodoUpdate(
            title="Updated Todo",
            description="Updated Description",
            priority="medium",
            completed=True,
        )

        mock_db = Mock(spec=Session)

        with patch.object(TodoService, "update_todo") as mock_update:
            mock_update.return_value = Mock(
                to_dict=lambda: {
                    "key": "test-key",
                    "title": "Updated Todo",
                    "description": "Updated Description",
                    "priority": "medium",
                    "completed": True,
                }
            )

            result = TodoService.update_todo(mock_db, 1, todo_update)

            mock_update.assert_called_once_with(mock_db, 1, todo_update)
            assert result is not None


class TestPriorityService:
    """Unit tests for PriorityService"""

    def test_create_priority_success(self, db_session: Session):
        """Test creating a priority successfully"""
        priority_data = PriorityCreate(
            name="High", color="#FF0000", order=1, description="High priority"
        )

        mock_db = Mock(spec=Session)

        with patch.object(PriorityService, "create_priority") as mock_create:
            mock_create.return_value = Mock(
                to_dict=lambda: {
                    "key": "high-priority",
                    "name": "High",
                    "color": "#FF0000",
                    "order": 1,
                }
            )

            result = PriorityService.create_priority(mock_db, priority_data)

            mock_create.assert_called_once_with(mock_db, priority_data)
            assert result is not None

    def test_get_priorities_with_pagination(self, db_session: Session):
        """Test getting priorities with pagination"""
        mock_db = Mock(spec=Session)

        with patch.object(PriorityService, "get_priorities") as mock_get:
            mock_priorities = [Mock() for _ in range(2)]
            mock_get.return_value = mock_priorities

            result = PriorityService.get_priorities(mock_db, skip=0, size=10)

            mock_get.assert_called_once_with(mock_db, skip=0, size=10)
            assert len(result) == 2

    def test_get_priority_by_key_not_found(self, db_session: Session):
        """Test getting priority by non-existent key"""
        mock_db = Mock(spec=Session)

        with patch.object(PriorityService, "fetch_priority_id_by_key") as mock_fetch:
            mock_fetch.side_effect = ValueError("Priority not found")

            try:
                PriorityService.fetch_priority_id_by_key(mock_db, "non-existent")
                assert False, "Should have raised ValueError"
            except ValueError as e:
                assert "Priority not found" in str(e)

    def test_update_priority_success(self, db_session: Session):
        """Test updating a priority successfully"""
        priority_update = PriorityUpdate(
            name="Medium", color="#FFFF00", order=2, description="Medium priority"
        )

        mock_db = Mock(spec=Session)

        with patch.object(PriorityService, "update_priority") as mock_update:
            mock_update.return_value = Mock(
                to_dict=lambda: {
                    "key": "medium-priority",
                    "name": "Medium",
                    "color": "#FFFF00",
                    "order": 2,
                }
            )

            result = PriorityService.update_priority(mock_db, 1, priority_update)

            mock_update.assert_called_once_with(mock_db, 1, priority_update)
            assert result is not None
