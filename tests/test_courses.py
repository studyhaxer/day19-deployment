from tests.conftest import register, auth_headers


class TestCreateCourse:
    def test_teacher_can_create_course_returns_201(self, client, teacher_headers):
        resp = client.post("/courses", json={"title": "Python 101"}, headers=teacher_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Python 101"
        assert "id" in data

    def test_student_cannot_create_course_returns_403(self, client, student_headers):
        resp = client.post("/courses", json={"title": "Sneaky Course"}, headers=student_headers)
        assert resp.status_code == 403

    def test_unauthenticated_cannot_create_course_returns_401(self, client):
        resp = client.post("/courses", json={"title": "No Auth Course"})
        assert resp.status_code == 401


class TestGetCourses:
    def test_get_courses_returns_list(self, client, teacher_headers, student_headers):
        client.post("/courses", json={"title": "Course A"}, headers=teacher_headers)
        client.post("/courses", json={"title": "Course B"}, headers=teacher_headers)
        resp = client.get("/courses", headers=student_headers)
        assert resp.status_code == 200
        titles = [c["title"] for c in resp.json()]
        assert "Course A" in titles
        assert "Course B" in titles

    def test_unauthenticated_cannot_get_courses_returns_401(self, client):
        resp = client.get("/courses")
        assert resp.status_code == 401