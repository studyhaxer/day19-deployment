import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from main import app

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    return TestClient(app)


def register(client, name="Test User", email="test@example.com", password="secret123", role="student"):
    return client.post("/register", json={
        "name": name, "email": email, "password": password, "role": role
    })


def login(client, email="test@example.com", password="secret123"):
    return client.post("/login", data={"username": email, "password": password})


def auth_headers(client, email="test@example.com", password="secret123"):
    token = login(client, email, password).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def student(client):
    register(client, name="Student", email="student@test.com", password="pass1234", role="student")
    return {"email": "student@test.com", "password": "pass1234"}


@pytest.fixture()
def teacher(client):
    register(client, name="Teacher", email="teacher@test.com", password="pass1234", role="teacher")
    return {"email": "teacher@test.com", "password": "pass1234"}


@pytest.fixture()
def student_headers(client, student):
    return auth_headers(client, student["email"], student["password"])


@pytest.fixture()
def teacher_headers(client, teacher):
    return auth_headers(client, teacher["email"], teacher["password"])