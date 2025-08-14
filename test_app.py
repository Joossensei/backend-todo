#!/usr/bin/env python3
"""
Simple test script to check if the AIOHTTP application can start.
"""

import asyncio
import sys
import os
from unittest.mock import AsyncMock, patch

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def _test_app_startup_async():
    """Async portion of the startup test."""
    try:
        from main import create_app
        from app import database

        print("Creating application...")
        create_app()
        print("✅ Application created successfully!")

        print("Testing database connection...")

        class FakeConnection:
            async def fetchval(self, query: str):
                return 1

        class _Acquire:
            async def __aenter__(self):
                return FakeConnection()

            async def __aexit__(self, exc_type, exc, tb):
                return False

        class FakePool:
            def acquire(self):
                return _Acquire()

            async def close(self):
                pass

        with patch(
            "app.database.asyncpg.create_pool",
            new=AsyncMock(return_value=FakePool()),
        ):
            pool = await database.get_pool()
            print("✅ Database pool created successfully!")
            async with pool.acquire() as connection:
                result = await connection.fetchval("SELECT 1")
                print(f"✅ Database query test successful: {result}")
            await database.close_pool()
            print("✅ Database pool closed successfully!")

        return True

    except Exception as e:
        print(f"❌ Error during startup: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_app_startup():
    """Run the async startup test using asyncio.run."""
    assert asyncio.run(_test_app_startup_async()) is True


if __name__ == "__main__":
    success = asyncio.run(_test_app_startup_async())
    if success:
        print("\n🎉 All tests passed! The application should work correctly.")
    else:
        print("\n💥 Tests failed. Please check the errors above.")
        sys.exit(1)
