from tests.conftest import register, auth_headers


class TestMe:
    def test_get_me_with_valid_token_returns_200(self, client, student, student_headers):
        resp = client.get("/me", headers=student_headers)
        assert resp.status_code == 200
        assert resp.json()["email"] == student["email"]

    def test_get_me_with_no_token_returns_401(self, client):
        resp = client.get("/me")
        assert resp.status_code == 401


class TestDashboard:
    def test_student_cannot_access_dashboard_returns_403(self, client, student_headers):
        resp = client.get("/dashboard", headers=student_headers)
        assert resp.status_code == 403

    def test_teacher_can_access_dashboard_returns_200(self, client, teacher_headers):
        resp = client.get("/dashboard", headers=teacher_headers)
        assert resp.status_code == 200


class TestGetUserById:
    def test_user_can_view_own_profile(self, client, student, student_headers):
        my_id = client.get("/me", headers=student_headers).json()["id"]
        resp = client.get(f"/users/{my_id}", headers=student_headers)
        assert resp.status_code == 200
        assert resp.json()["email"] == student["email"]

    def test_student_cannot_view_other_user_returns_403(self, client, student_headers, teacher, teacher_headers):
        teacher_id = client.get("/me", headers=teacher_headers).json()["id"]
        resp = client.get(f"/users/{teacher_id}", headers=student_headers)
        assert resp.status_code == 403


class TestDeleteUser:
    def test_user_can_delete_own_account(self, client):
        register(client, name="ToDelete", email="todelete@test.com", password="pass1234")
        headers = auth_headers(client, "todelete@test.com", "pass1234")
        user_id = client.get("/me", headers=headers).json()["id"]
        resp = client.delete(f"/users/{user_id}", headers=headers)
        assert resp.status_code == 200
        assert "deleted" in resp.json()["message"].lower()

    def test_user_cannot_delete_another_account_returns_403(self, client, student, teacher_headers):
        student_headers = auth_headers(client, student["email"], student["password"])
        student_id = client.get("/me", headers=student_headers).json()["id"]
        resp = client.delete(f"/users/{student_id}", headers=teacher_headers)
        assert resp.status_code == 403