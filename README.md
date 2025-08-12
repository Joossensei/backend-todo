# Todo API

## Setup

1. Clone the repository

```bash
git clone git@github.com:Joossensei/backend-todo.git
cd todo-app/backend
```

2. Create virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Set up environment variables

```bash
cp .env.example .env
# Edit .env with your actual values
```

5. Run the application

```bash
uvicorn app.main:app --reload
```

This approach ensures your repository stays clean, small, and portable across different environments!

# Todo API Documentation

## Rate limits

Throughout the API we have different Rate limits in place.

These rate limits all get served back to the user via the Response Headers:

- `x-ratelimit-limit`
- `x-ratelimit-remaining`
- `x-ratelimit-reset`

These headers contain the information necessary for the rate limiting on each endpoint.

If you're curious there is also a table all the way at the bottom of this document of all endpoints with their rate limit.

## Standard routes

### GET `/`

Root endpoint. Returns some info about the API

**Response:**

```json
{
  "message": "Welcome to Todo API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

### GET `/health`

Returns if the API is healthy.

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2025-08-12T08:15:26.707059Z"
}
```

## Authentication

### POST `/api/v1/token`

Authenticate the user with username and password and receive the JWT access token.

**Request Body:**

```json
{
  "username": "user",
  "password": "secret",
  "scope": "any",
  "grant_type": "password"
}
```

**Response Body:**

```json
{
  "access_token": "<access_token>",
  "token_type": "bearer",
  "expires_at": "2025-09-11T08:15:26.707059Z",
  "user_key": "aaaaaaaa-0000-aaaa-0000-aaaaaaaaaaaa"
}
```

---

## Todo routes

### GET `/api/v1/todos`

Get all todos for the authenticated user.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Query Parameters:**

1. `page` (int, optional): The page number to get.
   - **Default**: `1`.
2. `size` (int, optional): The number of todos to get per page
   - **Default**: `10`
   - Maximum: `100`
3. `sort` (constant values, optional): The type of sorting you want to do. Possible options
   - `?sort=priority-desc`: Sort by priority order desc
   - `?sort=priority-desc-text-asc`: Sort by priority order desc and text asc
   - `?sort=incomplete-priority-desc`: Sort by incomplete and priority order desc
   - `?sort=text-asc`: Sort by A-Z
   - `?sort=text-desc`: Sort by Z-A
   - **Default**: `incomplete-priority-desc`
4. `completed` (boolean, optional): Returns records depending on value
   - Empty: Returns all records
   - `true`: Returns all completed records
   - `false`: Returns all incomplete records
5. `priority` (str, optional): Returns records depending on value, expects priority key
   - Empty: Returns all records
   - `?priority={priorityKey}`: Returns all todo items with the defined priority
6. `search` (str, optional): Returns records depending on value
   - Empty: Returns all records
   - `?search=ABC`: Returns all records containing the text ABC (case insensitive)

**Response:**

```json
{
  "todos": [
    {
      "key": "aaaaaaaa-0000-aaaa-0000-aaaaaaaaaaaa",
      "title": "Test Todo",
      "description": "Very interesting description",
      "completed": false,
      "priority": "aaaaaaaa-0000-aaaa-0000-aaaaaaaaaaaa",
      "user_key": "aaaaaaaa-0000-aaaa-0000-aaaaaaaaaaaa",
      "created_at": "2025-08-12T08:26:31.453798Z",
      "updated_at": "2025-08-12T08:26:31.453798Z"
    }, ...
  ],
  "total": 180,
  "page": 3,
  "size": 10,
  "success": true,
  "next_link": "/todos?page=2&size=10",
  "prev_link": "/todos?page=4&size=10"
}
```

### GET `/api/v1/todos/{key}`

Endpoint for fetching a single todo for the authenticated user

**Path Parameters**

- `key`: The key of the Todo record you would like to fetch

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response Body:**

```json
{
  "key": "aaaaaaaa-0000-aaaa-0000-aaaaaaaaaaaa",
  "title": "Test Todo",
  "description": "Very interesting description",
  "completed": false,
  "priority": "aaaaaaaa-0000-aaaa-0000-aaaaaaaaaaaa",
  "user_key": "aaaaaaaa-0000-aaaa-0000-aaaaaaaaaaaa",
  "created_at": "2025-08-12T08:26:31.453798Z",
  "updated_at": "2025-08-12T08:26:31.453798Z"
}
```

### POST `/api/v1/todos`

Create a todo for the authenticated user

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request Body:**

```json
{
  "title": "Test Todo",
  "description": "Very interesting description",
  "priority": "aaaaaaaa-0000-aaaa-0000-aaaaaaaaaaaa",
  "completed": false,
  "user_key": "aaaaaaaa-0000-aaaa-0000-aaaaaaaaaaaa"
}
```

**Response Body:**

```json
{
  "key": "aaaaaaaa-0000-aaaa-0000-aaaaaaaaaaaa",
  "title": "Test Todo",
  "description": "Very interesting description",
  "completed": false,
  "priority": "aaaaaaaa-0000-aaaa-0000-aaaaaaaaaaaa",
  "user_key": "aaaaaaaa-0000-aaaa-0000-aaaaaaaaaaaa",
  "created_at": "2025-08-12T08:26:31.453798Z",
  "updated_at": null
}
```

### PUT `/api/v1/todos/{key}`

Update an entire todo for the authenticated user

**Path Parameters**

- `key`: The key of the Todo record you would like to update

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request Body:**

```json
{
  "title": "Test Todo edited",
  "description": "Testing Testing",
  "priority": "aaaaaaaa-0000-aaaa-0000-aaaaaaaaaaaa",
  "completed": true
}
```

**Response Body:**

```json
{
  "key": "aaaaaaaa-0000-aaaa-0000-aaaaaaaaaaaa",
  "title": "Test Todo edited",
  "description": "Testing Testing",
  "completed": true,
  "priority": "aaaaaaaa-0000-aaaa-0000-aaaaaaaaaaaa",
  "user_key": "aaaaaaaa-0000-aaaa-0000-aaaaaaaaaaaa",
  "created_at": "2025-08-12T08:26:31.453798Z",
  "updated_at": "2025-08-12T08:38:19.853610Z"
}
```

### PATCH `/api/v1/todos/{key}`

Update a single or multiple fields for a todo of the authenticated user

**Path Parameters**

- `key`: The key of the Todo record you would like to update

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request Body:**

_Note: All these fields are optional but you must provide at least **one**!_

```json
{
  "title": "Test Todo edited",
  "description": "Testing Testing",
  "priority": "aaaaaaaa-0000-aaaa-0000-aaaaaaaaaaaa",
  "completed": true
}
```

**Response Body:**

```json
{
  "key": "aaaaaaaa-0000-aaaa-0000-aaaaaaaaaaaa",
  "title": "Test Todo edited",
  "description": "Testing Testing",
  "completed": true,
  "priority": "aaaaaaaa-0000-aaaa-0000-aaaaaaaaaaaa",
  "user_key": "aaaaaaaa-0000-aaaa-0000-aaaaaaaaaaaa",
  "created_at": "2025-08-12T08:26:31.453798Z",
  "updated_at": "2025-08-12T08:38:19.853610Z"
}
```

### DELETE `/api/v1/todos/{key}`

Deletes a todo of the authenticated user

**Path Parameters**

- `key`: The key of the Todo record you would like to delete

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response Body:**

```json
{
  "message": "Todo deleted successfully"
}
```

---

## Priority routes

### GET `/api/v1/priorities`

Get all priorties for the authenticated user.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Query Parameters:**

1. `page` (int, optional): The page number to get.
   - Default is `1`.
2. `size` (int, optional): The number of prio's to get per page
   - Default: `10`
   - Maximum: `100`

**Response:**

```json
{
  "priorities": [
    {
      "key": "aaaaaaaa-0000-aaaa-0000-aaaaaaaaaaaa",
      "name": "Low",
      "description": "Low priority",
      "color": "#000000",
      "icon": "fa-lock",
      "order": 1,
      "user_key": "aaaaaaaa-0000-aaaa-0000-aaaaaaaaaaaa",
      "created_at": "2025-08-12T08:26:11.866058Z",
      "updated_at": null
    }
  ],
  "total": 180,
  "page": 3,
  "size": 10,
  "success": true,
  "next_link": "/priorities?page=2&size=10",
  "prev_link": "/priorities?page=4&size=10"
}
```

### GET `/api/v1/priorities/{key}`

Endpoint for fetching a single priority for the authenticated user

**Path Parameters**

- `key`: The key of the Priority record you would like to fetch

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response Body:**

```json
{
  "key": "aaaaaaaa-0000-aaaa-0000-aaaaaaaaaaaa",
  "name": "Low",
  "description": "Low priority",
  "color": "#000000",
  "icon": "fa-lock",
  "order": 1,
  "user_key": "aaaaaaaa-0000-aaaa-0000-aaaaaaaaaaaa",
  "created_at": "2025-08-12T08:26:11.866058Z",
  "updated_at": "2025-08-12T08:26:11.866058Z"
}
```

### POST `/api/v1/priorities`

Create a priority for the authenticated user

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request Body:**

```json
{
  "name": "Low",
  "description": "Low priority",
  "color": "#000000",
  "icon": "fa-lock",
  "order": 1,
  "user_key": "aaaaaaaa-0000-aaaa-0000-aaaaaaaaaaaa"
}
```

**Response Body:**

```json
{
  "key": "aaaaaaaa-0000-aaaa-0000-aaaaaaaaaaaa",
  "name": "Low",
  "description": "Low priority",
  "color": "#000000",
  "icon": "fa-lock",
  "order": 1,
  "user_key": "aaaaaaaa-0000-aaaa-0000-aaaaaaaaaaaa",
  "created_at": "2025-08-12T08:26:11.866058Z",
  "updated_at": null
}
```

### PUT `/api/v1/priorities/{key}`

Update an entire priority for the authenticated user

**Path Parameters**

- `key`: The key of the Priority record you would like to update

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request Body:**

```json
{
  "name": "Low",
  "description": "Low priority",
  "color": "#000000",
  "icon": "fa-lock",
  "order": 1
}
```

**Response Body:**

```json
{
  "key": "aaaaaaaa-0000-aaaa-0000-aaaaaaaaaaaa",
  "name": "Low",
  "description": "Low priority",
  "color": "#000000",
  "icon": "fa-lock",
  "order": 1,
  "user_key": "aaaaaaaa-0000-aaaa-0000-aaaaaaaaaaaa",
  "created_at": "2025-08-12T08:26:11.866058Z",
  "updated_at": "2025-08-12T08:56:11.240717Z"
}
```

### PATCH `/api/v1/priorities/{key}`

Update a single or multiple fields for a Priority of the authenticated user

**Path Parameters**

- `key`: The key of the Priority record you would like to update

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request Body:**

_Note: All these fields are optional but you must provide at least **one**!_

```json
{
  "name": "Low",
  "description": "Low priority",
  "color": "#000000",
  "icon": "fa-lock",
  "order": 1
}
```

**Response Body:**

```json
{
  "key": "aaaaaaaa-0000-aaaa-0000-aaaaaaaaaaaa",
  "name": "Low",
  "description": "Low priority",
  "color": "#000000",
  "icon": "fa-lock",
  "order": 1,
  "user_key": "aaaaaaaa-0000-aaaa-0000-aaaaaaaaaaaa",
  "created_at": "2025-08-12T08:26:11.866058Z",
  "updated_at": "2025-08-12T08:56:11.240717Z"
}
```

### DELETE `/api/v1/priorities/{key}`

Deletes a todo of the authenticated user

**Path Parameters**

- `key`: The key of the Todo record you would like to delete

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response Body:**

```json
{
  "message": "Priority deleted successfully"
}
```

---

## User routes

### GET `/api/v1/users`

Get all users.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Query Parameters:**

1. `page` (int, optional): The page number to get.
   - Default is `1`.
2. `size` (int, optional): The number of prio's to get per page
   - Default: `10`
   - Maximum: `100`

**Response:**

```json
{
  "users": [
    {
      "key": "aaaaaaaa-0000-aaaa-0000-aaaaaaaaaaaa",
      "name": "Test Gebruiker",
      "username": "test",
      "email": "test@example.com",
      "is_active": true,
      "created_at": "2025-08-11T07:48:34.301306Z",
      "updated_at": "2025-08-11T07:48:34.301306Z"
    }, ...
  ],
  "total": 180,
  "page": 3,
  "size": 10,
  "success": true,
  "next_link": "/users?page=2&size=10",
  "prev_link": "/users?page=4&size=10"
}
```

### GET `/api/v1/users/{key}`

Endpoint for fetching a single user

**Path Parameters**

- `key`: The key of the User record you would like to fetch

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response Body:**

```json
{
  "key": "aaaaaaaa-0000-aaaa-0000-aaaaaaaaaaaa",
  "name": "Test Gebruiker",
  "username": "test",
  "email": "test@example.com",
  "is_active": true,
  "created_at": "2025-08-11T07:48:34.301306Z",
  "updated_at": null
}
```

### POST `/api/v1/users`

Create a user. The password is hashed in the API and that is stored in the Database.

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request Body:**

```json
{
  "name": "I am new",
  "username": "newUser",
  "email": "new@user.com",
  "password": "verySecure",
  "is_active": true
}
```

**Response Body:**

```json
{
  "key": "aaaaaaaa-0000-aaaa-0000-aaaaaaaaaaaa",
  "name": "I am new",
  "username": "newUser",
  "email": "new@user.com",
  "is_active": true,
  "created_at": "2025-08-12T11:45:02.356045Z",
  "updated_at": null
}
```

### PUT `/api/v1/users/{key}`

Update an entire user except the Password. For this there is a seperate endpoint.

Rejects if you try to update a user that isn't yourself.

**Path Parameters**

- `key`: The key of the User record you would like to update

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request Body:**

```json
{
  "name": "Not new anymore",
  "email": "notnew@user.com",
  "is_active": true
}
```

**Response Body:**

```json
{
  "key": "aaaaaaaa-0000-aaaa-0000-aaaaaaaaaaaa",
  "name": "Not new anymore",
  "username": "newUser",
  "email": "notnew@user.com",
  "is_active": true,
  "created_at": "2025-08-12T11:45:02.356045Z",
  "updated_at": null
}
```

### PUT `/api/v1/users/{key}/password`

Update the password for the currently authenticated user

**Path Parameters**

- `key`: The key of the Priority record you would like to update

**Headers:**

```
Authorization: Bearer <access_token>
```

**Request Body:**

```json
{
  "current_password": "verySecure",
  "password": "notSecure"
}
```

**Response Body:**

```json
{
  "message": "User password updated successfully"
}
```

### DELETE `/api/v1/users/{key}`

Deletes a user

**Path Parameters**

- `key`: The key of the Todo record you would like to delete

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response Body:**

```json
{
  "message": "User deleted successfully"
}
```

---

# Rate limit table

| Method     | Path                           | Rate limit                       | Keying basis |
| ---------- | ------------------------------ | -------------------------------- | ------------ |
| **GET**    | `/`                            | 60 per minute                    | IP address   |
| **GET**    | `/health`                      | 60 per minute                    | IP address   |
| **POST**   | `/api/v1/token`                | 5 per minute and 100 per hour    | IP address   |
| **GET**    | `/api/v1/users`                | 10 per second and 200 per minute | User key     |
| **GET**    | `/api/v1/users/{key}`          | 20 per second and 400 per minute | User key     |
| **POST**   | `/api/v1/users`                | 5 per minute and 50 per hour     | IP address   |
| **PUT**    | `/api/v1/users/{key}`          | 10 per minute and 100 per hour   | User key     |
| **PUT**    | `/api/v1/users/{key}/password` | 10 per minute and 100 per hour   | User key     |
| **DELETE** | `/api/v1/users/{key}`          | 10 per minute and 50 per hour    | User key     |
| **GET**    | `/api/v1/todos`                | 10 per second and 200 per minute | User key     |
| **GET**    | `/api/v1/todos/{key}`          | 20 per second and 400 per minute | User key     |
| **POST**   | `/api/v1/todos`                | 10 per minute and 100 per hour   | User key     |
| **PUT**    | `/api/v1/todos/{key}`          | 20 per minute and 200 per hour   | User key     |
| **PATCH**  | `/api/v1/todos/{key}`          | 20 per minute and 200 per hour   | User key     |
| **DELETE** | `/api/v1/todos/{key}`          | 10 per minute and 50 per hour    | User key     |
| **GET**    | `/api/v1/priorities`           | 10 per second and 200 per minute | User key     |
| **GET**    | `/api/v1/priorities/{key}`     | 20 per second and 400 per minute | User key     |
| **POST**   | `/api/v1/priorities`           | 10 per minute and 100 per hour   | User key     |
| **PUT**    | `/api/v1/priorities/{key}`     | 20 per minute and 200 per hour   | User key     |
| **PATCH**  | `/api/v1/priorities/{key}`     | 20 per minute and 200 per hour   | User key     |
| **DELETE** | `/api/v1/priorities/{key}`     | 10 per minute and 50 per hour    | User key     |
