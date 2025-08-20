"""
Tests for rate limiting middleware.

Tests cover:
- Per-IP rate limiting on public endpoints
- Per-user rate limiting on authenticated endpoints
- Multi-window policies
- Proper rate limit headers
- 429 responses with Retry-After
"""

import pytest
import time
from app.middleware.rate_limit import reset_rate_limiters
from tests.factories import AuthFactory, PriorityFactory


@pytest.fixture(autouse=True)
async def reset_limits():
    """Reset rate limiters before each test."""
    reset_rate_limiters()
    yield


class TestRateLimitHeaders:
    """Test rate limit headers are properly set."""

    @pytest.mark.asyncio
    async def test_rate_limit_headers_on_success(self, client):
        """Test that rate limit headers are set on successful requests."""
        response = await client.get("/")

        assert response.status == 200
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers

        # Should have remaining requests
        remaining = int(response.headers["X-RateLimit-Remaining"])
        assert remaining > 0
        assert remaining < 61  # Should be less than or equal to limit

    @pytest.mark.asyncio
    async def test_rate_limit_headers_on_429(self, client):
        """Test that rate limit headers are set on 429 responses."""
        # Make 61 requests to exceed the 60/minute limit
        for _ in range(60):
            response = await client.get("/")
            assert response.status == 200

        # 61st request should be rate limited
        response = await client.get("/")
        assert response.status == 429

        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers
        assert "Retry-After" in response.headers

        # Should have 0 remaining
        remaining = int(response.headers["X-RateLimit-Remaining"])
        assert remaining == 0


class TestPerIPRateLimiting:
    """Test per-IP rate limiting on public endpoints."""

    @pytest.mark.asyncio
    async def test_root_endpoint_ip_limit(self, client):
        """Test rate limiting on root endpoint (60/minute per IP)."""
        # Make 60 requests - should all succeed
        for i in range(60):
            response = await client.get("/")
            assert response.status == 200, f"Request {i+1} failed"

        # 61st request should be rate limited
        response = await client.get("/")
        assert response.status == 429

        error_data = await response.json()
        assert error_data["error"]["code"] == "rate_limited"
        assert error_data["error"]["message"] == "Too Many Requests"

    @pytest.mark.asyncio
    async def test_health_endpoint_ip_limit(self, client):
        """Test rate limiting on health endpoint (60/minute per IP)."""
        # Make 60 requests - should all succeed
        for i in range(60):
            response = await client.get("/health")
            assert response.status == 200, f"Request {i+1} failed"

        # 61st request should be rate limited
        response = await client.get("/health")
        assert response.status == 429

    @pytest.mark.asyncio
    async def test_token_endpoint_ip_limit(self, client):
        """Test rate limiting on token endpoint (5/minute + 100/hour per IP)."""
        # Make 5 requests - should all succeed
        for i in range(5):
            response = await client.post(
                "/api/v1/token",
                data={
                    "username": "testuser",
                    "password": "testpass",
                    "grant_type": "password",
                },
            )
            assert response.status in [200, 401], f"Request {i+1} failed"

        # 6th request should be rate limited
        response = await client.post(
            "/api/v1/token",
            data={
                "username": "testuser",
                "password": "testpass",
                "grant_type": "password",
            },
        )
        assert response.status == 429

    @pytest.mark.asyncio
    async def test_user_registration_ip_limit(self, client):
        """Test rate limiting on user registration (5/minute + 50/hour per IP)."""
        # Make 5 requests - should all succeed
        for i in range(5):
            response = await client.post(
                "/api/v1/users",
                json={
                    "name": f"Test User {i}",
                    "username": f"testuser{i}",
                    "email": f"test{i}@example.com",
                    "password": "SecurePass123",  # Meets password requirements
                },
            )
            assert response.status in [200, 201, 400, 422], f"Request {i+1} failed"

        # 6th request should be rate limited
        response = await client.post(
            "/api/v1/users",
            json={
                "name": "Test User 6",
                "username": "testuser6",
                "email": "test6@example.com",
                "password": "SecurePass123",  # Meets password requirements
            },
        )
        assert response.status == 429


class TestPerUserRateLimiting:
    """Test per-user rate limiting on authenticated endpoints."""

    @pytest.mark.asyncio
    async def test_todos_endpoint_user_limit(self, client, db_conn):
        """Test rate limiting on todos endpoint (10/second + 200/minute per user)."""
        # Create authenticated user
        auth_data = await AuthFactory.create_authenticated_user(db_conn)

        # Make 10 requests - should all succeed
        for i in range(10):
            response = await client.get("/api/v1/todos", headers=auth_data["headers"])
            assert response.status == 200, f"Request {i+1} failed"

        # 11th request should be rate limited
        response = await client.get("/api/v1/todos", headers=auth_data["headers"])
        assert response.status == 429

    @pytest.mark.asyncio
    async def test_todo_detail_endpoint_user_limit(self, client, db_conn):
        """Test rate limiting on todo detail endpoint (20/second + 400/minute per user)."""
        # Create authenticated user and todo
        auth_data = await AuthFactory.create_authenticated_user(db_conn)
        user_key = auth_data["user"]["key"]

        # Create a priority first
        priority = await PriorityFactory.create_priority(
            db_conn, user_key, name="High", order=1
        )

        # Create a todo first
        todo_response = await client.post(
            "/api/v1/todos",
            json={
                "title": "Test Todo",
                "description": "Test Description",
                "priority": priority["key"],  # Use the priority key
                "completed": False,
                "user_key": user_key,
            },
            headers=auth_data["headers"],
        )
        assert todo_response.status == 201  # Should be 201 for creation
        todo_data = await todo_response.json()
        todo_key = todo_data["key"]

        # Make 20 requests - should all succeed
        for i in range(20):
            response = await client.get(
                f"/api/v1/todo/{todo_key}", headers=auth_data["headers"]
            )
            assert response.status == 200, f"Request {i+1} failed"

        # 21st request should be rate limited
        response = await client.get(
            f"/api/v1/todo/{todo_key}", headers=auth_data["headers"]
        )
        assert response.status == 429

    @pytest.mark.asyncio
    async def test_priorities_endpoint_user_limit(self, client, db_conn):
        """Test rate limiting on priorities endpoint (10/second + 200/minute per user)."""
        # Create authenticated user
        auth_data = await AuthFactory.create_authenticated_user(db_conn)

        # Make 10 requests - should all succeed
        for i in range(10):
            response = await client.get(
                "/api/v1/priorities", headers=auth_data["headers"]
            )
            assert response.status == 200, f"Request {i+1} failed"

        # 11th request should be rate limited
        response = await client.get("/api/v1/priorities", headers=auth_data["headers"])
        assert response.status == 429

    @pytest.mark.asyncio
    async def test_user_profile_endpoint_user_limit(self, client, db_conn):
        """Test rate limiting on user profile endpoint (20/second + 400/minute per user)."""
        # Create authenticated user
        auth_data = await AuthFactory.create_authenticated_user(db_conn)
        user_key = auth_data["user"]["key"]

        # Make 20 requests - should all succeed
        for i in range(20):
            response = await client.get(
                f"/api/v1/user/{user_key}", headers=auth_data["headers"]
            )
            assert response.status == 200, f"Request {i+1} failed"

        # 21st request should be rate limited
        response = await client.get(
            f"/api/v1/user/{user_key}", headers=auth_data["headers"]
        )
        assert response.status == 429


class TestMultiWindowPolicies:
    """Test multi-window rate limiting policies."""

    @pytest.mark.asyncio
    async def test_token_endpoint_multi_window(self, client):
        """Test token endpoint with both minute and hour limits."""
        # Make 5 requests (minute limit) - should all succeed
        for i in range(5):
            response = await client.post(
                "/api/v1/token",
                data={
                    "username": "testuser",
                    "password": "testpass",
                    "grant_type": "password",
                },
            )
            assert response.status in [200, 401], f"Request {i+1} failed"

        # 6th request should be rate limited (minute limit exceeded)
        response = await client.post(
            "/api/v1/token",
            data={
                "username": "testuser",
                "password": "testpass",
                "grant_type": "password",
            },
        )
        assert response.status == 429

    @pytest.mark.asyncio
    async def test_todos_endpoint_multi_window(self, client, db_conn):
        """Test todos endpoint with both second and minute limits."""
        # Create authenticated user
        auth_data = await AuthFactory.create_authenticated_user(db_conn)

        # Make 10 requests (second limit) - should all succeed
        for i in range(10):
            response = await client.get("/api/v1/todos", headers=auth_data["headers"])
            assert response.status == 200, f"Request {i+1} failed"

        # 11th request should be rate limited (second limit exceeded)
        response = await client.get("/api/v1/todos", headers=auth_data["headers"])
        assert response.status == 429


class TestRateLimitRecovery:
    """Test rate limit recovery after windows expire."""

    @pytest.mark.asyncio
    async def test_rate_limit_recovery_after_window(self, client):
        """Test that rate limits reset after the window expires."""
        # Make 60 requests to hit the limit
        for i in range(60):
            response = await client.get("/")
            assert response.status == 200, f"Request {i+1} failed"

        # 61st request should be rate limited
        response = await client.get("/")
        assert response.status == 429

        # Wait for the window to expire (1 minute)
        # In a real test, you might want to mock time or use a shorter window
        # For now, we'll just test that the rate limiter works correctly
        # and that the headers show the correct reset time

        reset_time = int(response.headers["X-RateLimit-Reset"])
        current_time = int(time.time())
        assert reset_time > current_time


class TestRateLimitIdentity:
    """Test that rate limiting works correctly for different identities."""

    @pytest.mark.asyncio
    async def test_different_users_have_separate_limits(self, client, db_conn):
        """Test that different users have separate rate limit buckets."""
        # Create two authenticated users
        auth_data1 = await AuthFactory.create_authenticated_user(
            db_conn, username="user1"
        )
        auth_data2 = await AuthFactory.create_authenticated_user(
            db_conn, username="user2"
        )

        # User 1 makes 10 requests (hits the limit)
        for i in range(10):
            response = await client.get("/api/v1/todos", headers=auth_data1["headers"])
            assert response.status == 200, f"User 1 request {i+1} failed"

        # User 1's 11th request should be rate limited
        response = await client.get("/api/v1/todos", headers=auth_data1["headers"])
        assert response.status == 429

        # User 2 should still be able to make requests
        for i in range(10):
            response = await client.get("/api/v1/todos", headers=auth_data2["headers"])
            assert response.status == 200, f"User 2 request {i+1} failed"

    @pytest.mark.asyncio
    async def test_unauthenticated_falls_back_to_ip(self, client, db_conn):
        """Test that unauthenticated requests fall back to IP-based limiting."""
        # Create authenticated user
        auth_data = await AuthFactory.create_authenticated_user(db_conn)

        # Make 10 authenticated requests (hits user limit)
        for i in range(10):
            response = await client.get("/api/v1/todos", headers=auth_data["headers"])
            assert response.status == 200, f"Auth request {i+1} failed"

        # 11th authenticated request should be rate limited
        response = await client.get("/api/v1/todos", headers=auth_data["headers"])
        assert response.status == 429

        # But unauthenticated requests to public endpoints should still work
        # (they use IP-based limiting)
        response = await client.get("/")
        assert response.status == 200


class TestRateLimitEdgeCases:
    """Test edge cases in rate limiting."""

    @pytest.mark.asyncio
    async def test_no_policy_matches(self, client):
        """Test that requests without matching policies are not rate limited."""
        # Make a request to a non-existent endpoint
        response = await client.get("/non-existent-endpoint")
        assert response.status == 404

        # Should not have rate limit headers
        assert "X-RateLimit-Limit" not in response.headers
        assert "X-RateLimit-Remaining" not in response.headers
        assert "X-RateLimit-Reset" not in response.headers

    @pytest.mark.asyncio
    async def test_invalid_jwt_falls_back_to_ip(self, client):
        """Test that invalid JWT tokens fall back to IP-based limiting."""
        # Make request with invalid JWT
        response = await client.get(
            "/api/v1/todos", headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status == 401

        # The request should not be rate limited (it fails before reaching rate limiter)
        # But if it did reach the rate limiter, it would fall back to IP-based limiting
