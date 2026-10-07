"""Isolated FastAPI test fixtures; tests never touch the developer's SQLite file."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.middleware.rate_limit import _hits
from app.services.ai_service import ai_service


def sample_questions(generation: int = 1):
    return [
        {
            "question": f"Generation {generation}: Which answer is correct for item {number}?",
            "options": {
                "A": f"First choice {number}",
                "B": f"Second choice {number}",
                "C": f"Third choice {number}",
                "D": f"Fourth choice {number}",
            },
            "correct_answer": "A",
            "explanation": f"Choice A is correct for item {number}.",
        }
        for number in range(1, 11)
    ]


@pytest.fixture
def client(monkeypatch):
    _hits.clear()
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    monkeypatch.setattr("app.main.create_tables", lambda: None)

    generation = {"number": 0}

    def generate_questions(subject, difficulty):
        generation["number"] += 1
        return {
            "subject": subject,
            "difficulty": difficulty,
            "questions": sample_questions(generation["number"]),
            "source": "ai",
        }

    monkeypatch.setattr(ai_service, "generate_questions", generate_questions)
    monkeypatch.setattr(ai_service, "generate_feedback", lambda *args, **kwargs: "Review your missed concepts and keep practicing.")

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    engine.dispose()


@pytest.fixture
def register_user(client):
    def register(email="candidate@example.com", name="Candidate User"):
        response = client.post(
            "/api/auth/register",
            json={"name": name, "email": email, "password": "SufficientPass9!"},
        )
        assert response.status_code == 201, response.text
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}, response.json()["user"]
    return register
