"""ORM models are no longer automatically imported.

The application now interacts with the database using raw SQL through
``asyncpg``. Import models directly from their modules if needed.
"""

__all__: list[str] = []
