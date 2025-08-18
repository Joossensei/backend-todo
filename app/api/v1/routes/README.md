# Route Organization

This directory contains all route definitions for the API v1, organized by resource type.

## Structure

```
app/aiohttp/api/v1/routes/
├── __init__.py              # Exports all route functions
├── base.py                  # Base routes (health, root)
├── auth.py                  # Authentication routes
├── todos.py                 # Todo management routes
├── priorities.py            # Priority management routes
├── users.py                 # User management routes
└── README.md                # This file
```

## Route Organization Principles

### 1. **Resource-Based Organization**

Each resource type has its own route file:

- `todos.py` - All todo-related routes
- `priorities.py` - All priority-related routes
- `users.py` - All user-related routes
- `auth.py` - Authentication routes
- `base.py` - Basic API routes (health, root)

### 2. **Consistent Function Naming**

Each route file exports an `apply_*_routes()` function:

- `apply_todo_routes(routes)`
- `apply_priority_routes(routes)`
- `apply_user_routes(routes)`
- `apply_auth_routes(routes)`
- `apply_base_routes(routes)`

### 3. **Clear Documentation**

Each route has a descriptive docstring explaining its purpose.

## Route Registration

### Centralized Registration

All routes are registered through the `route_manager.py`:

```python
from app.api.v1.route_manager import register_all_routes

routes = register_all_routes()
app.add_routes(routes)
```

### Registration Order

Routes are registered in logical order:

1. **Base routes** - Health checks, root endpoint
2. **Auth routes** - Authentication endpoints
3. **Todo routes** - Todo management
4. **Priority routes** - Priority management
5. **User routes** - User management

## Adding New Routes

### 1. Create a New Resource Route File

```python
# app/aiohttp/api/v1/routes/categories.py
from aiohttp import web
from app.api.v1.endpoints import categories

def apply_category_routes(routes: web.RouteTableDef) -> None:
    """Apply category routes to the route table."""

    @routes.get("/api/v1/categories")
    async def get_categories(request: web.Request):
        """Get list of categories."""
        return await categories.get_categories(request)

    @routes.post("/api/v1/categories")
    async def create_category(request: web.Request):
        """Create a new category."""
        return await categories.create_category(request)
```

### 2. Update the Routes Package

```python
# app/aiohttp/api/v1/routes/__init__.py
from .categories import apply_category_routes

__all__ = [
    # ... existing exports
    "apply_category_routes",
]
```

### 3. Update the Route Manager

```python
# app/aiohttp/api/v1/route_manager.py
from .routes import (
    # ... existing imports
    apply_category_routes,
)

def register_all_routes() -> web.RouteTableDef:
    routes = web.RouteTableDef()

    # ... existing registrations
    apply_category_routes(routes)

    return routes
```

## Route Patterns

### RESTful Routes

Follow RESTful conventions:

- `GET /api/v1/resource` - List resources
- `GET /api/v1/resource/{id}` - Get specific resource
- `POST /api/v1/resource` - Create resource
- `PUT /api/v1/resource/{id}` - Update resource
- `PATCH /api/v1/resource/{id}` - Partial update
- `DELETE /api/v1/resource/{id}` - Delete resource

### Custom Routes

For non-RESTful operations, use descriptive paths:

- `POST /api/v1/user/{key}/password` - Update password
- `POST /api/v1/token` - Authentication

## Best Practices

### 1. **Keep Routes Simple**

Routes should only handle:

- URL parameter extraction
- Basic validation
- Delegation to endpoint functions

### 2. **Use Descriptive Names**

Route function names should clearly indicate their purpose:

```python
async def get_todo_by_key(request: web.Request):  # Good
async def get_todo(request: web.Request):         # Less clear
```

### 3. **Document Routes**

Each route should have a docstring:

```python
@routes.get("/api/v1/todos")
async def get_todos(request: web.Request):
    """Get paginated list of todos for the authenticated user."""
    return await todos.get_todos(request)
```

### 4. **Group Related Routes**

Keep related routes together in the same file:

- All todo routes in `todos.py`
- All user routes in `users.py`

### 5. **Consistent Error Handling**

Let the endpoint functions handle errors, routes should just delegate.

## Testing Routes

Test routes by creating test requests:

```python
async def test_get_todos():
    app = web.Application()
    routes = register_all_routes()
    app.add_routes(routes)

    # Test the route
    async with app.test_client() as client:
        resp = await client.get("/api/v1/todos")
        assert resp.status == 200
```

## Benefits of This Organization

1. **Maintainability**: Easy to find and modify routes for specific resources
2. **Scalability**: Easy to add new resources without cluttering existing files
3. **Team Collaboration**: Multiple developers can work on different resource routes
4. **Testing**: Routes can be tested independently
5. **Documentation**: Clear structure makes it easy to understand the API
6. **Reusability**: Route functions can be reused in different contexts

## Migration from Old Structure

The old structure had all routes in one file (`api.py`). The new structure:

1. **Separates concerns** by resource type
2. **Reduces file size** and complexity
3. **Improves readability** and maintainability
4. **Makes testing easier** with focused route files
5. **Enables better team collaboration**

The `apply_endpoints()` function in `api.py` is kept for backward compatibility but now delegates to the route manager.
