from tests.conftest import register, login


class TestRegister:
    def test_register_new_user_successfully(self, client):
        resp = register(client, name="Alice", email="alice@example.com", password="strongpass1")
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "alice@example.com"
        assert data["name"] == "Alice"
        assert "id" in data
        assert "hashed_password" not in data

    def test_register_duplicate_email_returns_400(self, client):
        register(client, email="dup@example.com")
        resp = register(client, email="dup@example.com")
        assert resp.status_code == 400
        assert "already registered" in resp.json()["detail"].lower()

    def test_login_with_correct_credentials_returns_token(self, client):
        register(client, email="user@example.com", password="mypassword")
        resp = login(client, email="user@example.com", password="mypassword")
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_with_wrong_password_returns_401(self, client):
        register(client, email="user2@example.com", password="correctpass")
        resp = login(client, email="user2@example.com", password="wrongpass")
        assert resp.status_code == 401
        assert "invalid" in resp.json()["detail"].lower()