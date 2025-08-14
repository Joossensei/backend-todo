# app/database.py
import asyncpg
from app.core.config import settings
from typing import Optional

# Global connection pool
_pool: Optional[asyncpg.Pool] = None


async def get_pool() -> asyncpg.Pool:
    """Get the database connection pool."""
    global _pool
    if _pool is None:
        # Convert SQLAlchemy URL to asyncpg format
        url = settings.database_url
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgres://")

        _pool = await asyncpg.create_pool(
            url, min_size=5, max_size=20, command_timeout=60
        )
    return _pool


async def close_pool():
    """Close the database connection pool."""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


async def get_db():
    """Get a database connection from the pool."""
    pool = await get_pool()
    async with pool.acquire() as connection:
        yield connection
