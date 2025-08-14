# app/api/v1/endpoints/priorities.py
from aiohttp import web
from app.services.priority_service import PriorityService
from app.database import get_db
from app.schemas.priority import PriorityResponse, PriorityListResponse
from app.api.deps import get_current_active_user


def setup_routes(app: web.Application, cors, prefix: str):
    """Setup priorities routes."""

    # Get priorities
    async def get_priorities_handler(request: web.Request):
        """Get priorities with pagination."""
        try:
            page = int(request.query.get("page", 1))
            size = int(request.query.get("size", 10))

            current_user = await get_current_active_user(request)

            pool = await get_db()
            async with pool.acquire() as connection:
                skip = (page - 1) * size
                priorities = await PriorityService.get_priorities(
                    connection, current_user.key, skip, size
                )
                total = await PriorityService.get_total_priorities(
                    connection, current_user.key
                )

                return web.json_response(
                    PriorityListResponse(
                        priorities=[
                            PriorityResponse(**priority) for priority in priorities
                        ],
                        total=total,
                        page=page,
                        size=len(priorities),
                        success=True,
                        next_link=(
                            f"/priorities?page={page + 1}&size={size}"
                            if page * size < total
                            else None
                        ),
                        prev_link=(
                            f"/priorities?page={page - 1}&size={size}"
                            if page > 1
                            else None
                        ),
                    ).dict()
                )

        except Exception as e:
            return web.json_response(
                {"detail": f"Internal server error: {str(e)}"}, status=500
            )

    # Add routes
    app.router.add_get(f"{prefix}", get_priorities_handler)

    # Setup CORS for all routes
    for route in app.router.routes():
        if route.resource.canonical.startswith(prefix):
            cors.add(route)
