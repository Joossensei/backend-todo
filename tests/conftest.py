import pytest
import pytest_asyncio
from aiohttp import web
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from db.database import Base
from main_aiohttp import create_app
from app.core.config import settings
from app.middleware.rate_limit import reset_rate_limiters
from tests.factories import AuthFactory


engine = create_engine(
    settings.test_database_url,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# DB Fixtures
@pytest.fixture(scope="function")
def db():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def test_db_url():
    """Get test database URL"""
    # Use environment variable or default to test DB
    return settings.test_database_url


@pytest_asyncio.fixture(scope="function", autouse=True)
async def reset_rate_limits():
    """Reset rate limiters before each test to prevent rate limiting issues"""
    reset_rate_limiters()
    yield


@pytest_asyncio.fixture(scope="function", autouse=True)
async def reset_db(app):
    """Ensure a clean database before each test.

    Connect directly using asyncpg to avoid depending on app startup hooks.
    The app fixture ensures settings.database_url points to the encoded test DB URL.
    """
    import asyncpg
    from app.core.config import settings as _settings

    conn = await asyncpg.connect(dsn=_settings.database_url)
    try:
        await conn.execute(
            "TRUNCATE TABLE todos, priorities, users RESTART IDENTITY CASCADE;"
        )
    finally:
        await conn.close()
    yield


@pytest_asyncio.fixture
async def db_conn(app):
    """Provide database connection with transaction rollback"""
    pool = app["db_pool"]
    async with pool.acquire() as conn:
        # Yield a regular connection; we rely on reset_db for cleanup between tests
        yield conn


# App Fixtures
@pytest.fixture
def app():
    """Create app with test database"""
    # Override settings for test database
    from app.core.config import settings
    import urllib.parse

    original_url = settings.database_url

    # URL encode the test database URL to handle special characters like #
    test_url = settings.test_database_url

    # Manually encode the password part before parsing since # breaks urlparse
    # Find the password part between : and @
    if "://" in test_url and "@" in test_url:
        scheme_part, rest = test_url.split("://", 1)
        if "@" in rest:
            credentials, host_part = rest.split("@", 1)
            if ":" in credentials:
                username, password = credentials.split(":", 1)
                # URL encode the password
                password = urllib.parse.quote(password, safe="")
                test_url = f"{scheme_part}://{username}:{password}@{host_part}"

    settings.database_url = test_url

    app = create_app()

    yield app

    # Restore original settings
    settings.database_url = original_url


# Client Fixtures
@pytest_asyncio.fixture
async def client(app: web.Application, aiohttp_client):
    """Create a test client for the app"""
    return await aiohttp_client(app)


@pytest_asyncio.fixture
async def auth_client(client, db_conn):
    """Create an authenticated test client"""
    auth_data = await AuthFactory.create_authenticated_user(
        db_conn, username="authenticated_user"
    )
    client.session.headers.update(
        {
            "Authorization": f"Bearer {auth_data['token']}",
            "User-Key": auth_data["user"]["key"],
        }
    )
    return client
