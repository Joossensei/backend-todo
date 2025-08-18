import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from d.database import get_db, Base
from main import app


# Test database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override the database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override the database dependency
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with a fresh database"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_todo_data():
    """Sample todo data for testing - priority will be set dynamically"""
    return {
        "title": "Test Todo",
        "description": "Test Description",
        "completed": False,
    }


@pytest.fixture
def sample_priority_data():
    """Sample priority data for testing"""
    return {
        "name": "High",
        "description": "High priority tasks",
        "color": "#FF0000",
        "order": 1,
    }


@pytest.fixture
def created_priority_key(client, sample_priority_data):
    """Create a priority and return its key for use in todo tests"""
    response = client.post("/api/v1/priorities/", json=sample_priority_data)
    assert response.status_code == 200
    priority_data = response.json()
    return priority_data["key"]


@pytest.fixture
def sample_todo_with_priority_data(created_priority_key):
    """Sample todo data with a valid priority key"""
    return {
        "title": "Test Todo",
        "description": "Test Description",
        "priority": created_priority_key,
        "completed": False,
    }


@pytest.fixture
def sample_todo_update_data(created_priority_key):
    """Sample todo update data for testing"""
    return {
        "title": "Updated Todo",
        "description": "Updated Description",
        "priority": created_priority_key,
        "completed": True,
    }


@pytest.fixture
def sample_priority_update_data():
    """Sample priority update data for testing"""
    return {
        "name": "Medium",
        "description": "Medium priority tasks",
        "color": "#FFFF00",
        "order": 2,
    }
