# app/core/errors.py
from aiohttp import web


class AppError(Exception):
    status = 400
    code = "bad_request"
    message = "Bad request"

    def to_response(self, request_id: str) -> web.Response:
        return web.json_response(
            {
                "error": {"code": self.code, "message": self.message},
                "request_id": request_id,
            },
            status=self.status,
        )


class NotFoundError(AppError):
    status = 404
    code = "not_found"
    message = "Resource not found"


class UnauthorizedError(AppError):
    status = 401
    code = "unauthorized"
    message = "Unauthorized"
