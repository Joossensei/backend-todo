#!/usr/bin/env python3
"""
Simple test script to check if the AIOHTTP application can start.
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def test_app_startup():
    """Test if the application can start without errors."""
    try:
        from main import create_app

        print("Creating application...")
        create_app()
        print("✅ Application created successfully!")

        print("Testing database connection...")
        from app.database import get_pool, close_pool

        pool = await get_pool()
        print("✅ Database pool created successfully!")

        # Test a simple query
        async with pool.acquire() as connection:
            result = await connection.fetchval("SELECT 1")
            print(f"✅ Database query test successful: {result}")

        await close_pool()
        print("✅ Database pool closed successfully!")

        return True

    except Exception as e:
        print(f"❌ Error during startup: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_app_startup())
    if success:
        print("\n🎉 All tests passed! The application should work correctly.")
    else:
        print("\n💥 Tests failed. Please check the errors above.")
        sys.exit(1)
