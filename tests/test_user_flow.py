from fastapi.testclient import TestClient


class TestUserIntegrationFlow:
    def test_full_user_flow(self, client: TestClient):
        # 1) Create user
        new_user = {
            "name": "Alice Example",
            "username": "alice",
            "email": "alice@example.com",
            "password": "StrongPassw0rd!",
            "is_active": True,
        }
        resp = client.post("/api/v1/users/", json=new_user)
        assert resp.status_code == 201
        created_user = resp.json()
        assert created_user["username"] == new_user["username"]
        user_key = created_user["key"]

        # 2) Login
        form = {
            "username": new_user["username"],
            "password": new_user["password"],
            "grant_type": "password",
        }
        login = client.post("/api/v1/token", data=form)
        assert login.status_code == 200
        token = login.json()["access_token"]
        assert token
        assert login.json()["user_key"] == user_key
        alice_headers = {"Authorization": f"Bearer {token}"}

        # 3) Read user
        get_user = client.get(f"/api/v1/users/{user_key}", headers=alice_headers)
        assert get_user.status_code == 200
        assert get_user.json()["username"] == new_user["username"]

        # 4) Update user (name + email)
        update_payload = {
            "name": "Alice Updated",
            "email": "alice.updated@example.com",
            "is_active": True,
        }
        update = client.put(
            f"/api/v1/users/{user_key}", headers=alice_headers, json=update_payload
        )
        assert update.status_code == 200
        updated_user = update.json()
        assert updated_user["name"] == update_payload["name"]
        assert updated_user["email"] == update_payload["email"]

        # 5) Update password
        pw_update_payload = {
            "current_password": new_user["password"],
            "password": "NewStrongerPassw0rd!",
        }
        pw_update = client.put(
            f"/api/v1/users/{user_key}/password",
            headers=alice_headers,
            json=pw_update_payload,
        )
        assert pw_update.status_code == 200
        assert "message" in pw_update.json()

        # 6) Delete user (use Alice's token while it's still valid)
        delete = client.delete(f"/api/v1/users/{user_key}", headers=alice_headers)
        assert delete.status_code in (200, 204)

        # 7) Login as a separate test user to perform the final check
        test_user = {
            "name": "Test User",
            "username": "test",
            "email": "test@example.com",
            "password": "Test123",
            "is_active": True,
        }
        create_test_user = client.post("/api/v1/users/", json=test_user)
        assert create_test_user.status_code == 201

        test_login = client.post(
            "/api/v1/token",
            data={
                "username": test_user["username"],
                "password": test_user["password"],
                "grant_type": "password",
            },
        )
        assert test_login.status_code == 200
        test_headers = {"Authorization": f"Bearer {test_login.json()['access_token']}"}

        # 8) Verify Alice is gone using a valid token
        get_after_delete = client.get(f"/api/v1/users/{user_key}", headers=test_headers)
        print(get_after_delete.json())
        assert get_after_delete.status_code == 404
