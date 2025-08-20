# app/core/errors.py
from aiohttp import web


class AppError(Exception):
    status = 400
    code = "bad_request"
    message = "Bad request"
    custom_message = None

    def __init__(self, error=None, custom_message=None):
        super().__init__()
        if custom_message:
            self.custom_message = custom_message
        elif error and hasattr(error, "args") and error.args:
            self.custom_message = str(error.args[0])
        elif error:
            self.custom_message = str(error)

    def to_response(self, request_id: str) -> web.Response:
        return web.json_response(
            {
                "error": {
                    "code": self.code,
                    "message": self.custom_message or self.message,
                },
                "request_id": request_id,
            },
            status=self.status,
        )


class NotFoundError(AppError):
    status = 404
    code = "not_found"
    message = "Resource not found"


class ValidationError(AppError):
    """
    Custom validation error that supports custom error messages.

    Usage examples:

    ### Method 1: Pass a custom message directly
    raise ValidationError(custom_message="Email format is invalid")

    ### Method 2: Pass an existing exception (current usage)
    raise ValidationError(ValueError("Order must be greater than 0"))

    ### Method 3: Pass any object that can be converted to string
    raise ValidationError("Field is required")

    ### Method 4: Pass both error and custom message (custom message takes precedence)
    raise ValidationError(ValueError("Original error"), "Custom message")
    """

    status = 422
    code = "validation_error"
    message = "Validation error"


class UnauthorizedError(AppError):
    status = 401
    code = "unauthorized"
    message = "Unauthorized"
