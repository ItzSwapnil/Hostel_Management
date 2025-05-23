import pytest
from app import create_app
from app.models.student import Student
from app.utils.database import db

@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
    yield app

def test_create_student(app):
    with app.test_client() as client:
        response = client.post("/api/v1/students/", json={
            "name": "Alice",
            "email": "alice@example.com"
        })
        assert response.status_code == 201