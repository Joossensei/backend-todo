# Middleware Organization

This directory contains all middleware functions for the AioHTTP application, organized by functionality.

## Structure

```
app/aiohttp/middleware/
├── __init__.py              # Exports all middleware functions
├── config.py                # Middleware configuration and ordering
├── error_handling.py        # Error handling and logging middleware
├── database.py              # Database connection middleware
├── authentication.py        # Authentication and authorization middleware
├── cors.py                  # CORS handling middleware
├── logging.py               # Request/response logging middleware
└── README.md                # This file
```

## Middleware Functions

### 1. Error Handling (`error_handling.py`)

- **`error_middleware`**: Global exception handler that converts all exceptions to appropriate HTTP responses
- Catches `web.HTTPException` and general exceptions
- Logs errors for debugging and monitoring
- Applies CORS headers to error responses

### 2. Database (`database.py`)

- **`db_connection_middleware`**: Provides database connection to each request
- Uses AsyncPG connection pool
- Ensures proper connection cleanup after request processing

### 3. Authentication (`authentication.py`)

- **`auth_parsing_middleware`**: Parses and validates JWT tokens
- **`require_auth`**: Decorator for enforcing authentication on specific routes
- Supports scope-based authorization
- Sets `user` and `claims` in request for downstream handlers

### 4. CORS (`cors.py`)

- **`make_cors_middleware`**: Factory function that creates CORS middleware
- **`_apply_cors`**: Helper function for applying CORS headers to responses
- Handles preflight requests (OPTIONS)
- Configurable allowed origins, credentials, and headers

### 5. Logging (`logging.py`)

- **`request_logging_middleware`**: Logs incoming requests and responses
- Includes timing information and user agent details
- Useful for monitoring and debugging

## Usage

### Basic Usage

```python
from app.middleware.config import get_middleware_stack

app = web.Application(middlewares=get_middleware_stack())
```

### Custom Middleware Stack

```python
from app.middleware import (
    error_middleware,
    db_connection_middleware,
    auth_parsing_middleware,
    make_cors_middleware,
)

# Create custom CORS middleware
cors_middleware = make_cors_middleware(
    allowed_origins=["http://localhost:3000"],
    allow_credentials=True,
)

app = web.Application(
    middlewares=[
        cors_middleware,
        error_middleware,
        db_connection_middleware,
        auth_parsing_middleware,
    ]
)
```

### Using Authentication Decorator

```python
from app.middleware.authentication import require_auth

@routes.get("/protected")
@require_auth(scopes=["read:users"])
async def protected_endpoint(request: web.Request):
    user = request["user"]
    return web.json_response({"message": f"Hello {user}!"})
```

## Middleware Order

The order of middleware is important. Here's the recommended order:

1. **CORS** (outermost) - Handles preflight requests before other middleware
2. **Error Handling** - Catches exceptions from all downstream middleware
3. **Request Logging** - Logs all requests and responses
4. **Database Connection** - Provides DB connection to handlers
5. **Authentication** (innermost) - Validates tokens and sets user context

## Best Practices

1. **Keep middleware focused**: Each middleware should have a single responsibility
2. **Use descriptive names**: Middleware names should clearly indicate their purpose
3. **Document middleware**: Include docstrings explaining what each middleware does
4. **Handle errors gracefully**: Middleware should not crash the application
5. **Consider performance**: Middleware runs on every request, so keep it efficient
6. **Test middleware**: Write tests for your middleware functions
7. **Use configuration**: Make middleware configurable through settings

## Adding New Middleware

To add new middleware:

1. Create a new file in the `middleware/` directory
2. Define your middleware function with the `@web.middleware` decorator
3. Add it to `__init__.py` exports
4. Update `config.py` to include it in the middleware stack
5. Update this README with documentation

Example:

```python
# app/aiohttp/middleware/custom.py
from aiohttp import web

@web.middleware
async def custom_middleware(request: web.Request, handler):
    # Your middleware logic here
    response = await handler(request)
    # Post-processing logic here
    return response
```

## Testing Middleware

Test your middleware by creating test requests and verifying the expected behavior:

```python
async def test_custom_middleware():
    app = web.Application(middlewares=[custom_middleware])
    # Add routes and test logic
```

## Configuration

Middleware configuration is centralized in `config.py` and uses settings from `app.core.config`. This makes it easy to:

- Change middleware behavior based on environment
- Enable/disable middleware for different deployments
- Configure middleware parameters through environment variables
