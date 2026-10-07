"""Verify the startup migration against the previous assessment schema."""

from sqlalchemy import create_engine, inspect, text

from app import database


def test_legacy_assessments_are_migrated_without_losing_rows(monkeypatch):
    engine = create_engine("sqlite://")
    with engine.begin() as connection:
        connection.execute(text(
            "CREATE TABLE users ("
            "id INTEGER PRIMARY KEY, name VARCHAR(255) NOT NULL, "
            "email VARCHAR(255) NOT NULL, password_hash VARCHAR(255) NOT NULL, "
            "is_active BOOLEAN, created_at DATETIME NOT NULL)"
        ))
        connection.execute(text(
            "CREATE TABLE assessments ("
            "id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, subject VARCHAR(100) NOT NULL, "
            "difficulty VARCHAR(50) NOT NULL, status VARCHAR(50), score INTEGER, "
            "correct_count INTEGER, wrong_count INTEGER, unanswered_count INTEGER, "
            "percentage FLOAT, performance VARCHAR(50), ai_feedback TEXT, "
            "created_at DATETIME NOT NULL, submitted_at DATETIME, final_submitted_at DATETIME)"
        ))
        connection.execute(text(
            "INSERT INTO users (id, name, email, password_hash, is_active, created_at) "
            "VALUES (1, 'Candidate', 'candidate@example.com', 'hash', 1, '2024-01-01')"
        ))
        connection.execute(text(
            "INSERT INTO assessments (id, user_id, subject, difficulty, status, score, "
            "correct_count, wrong_count, unanswered_count, percentage, performance, created_at) "
            "VALUES (27, 1, 'Python', 'Intermediate', 'submitted', 9, 9, 1, 0, 90, 'Excellent', '2024-01-01')"
        ))

    monkeypatch.setattr(database, "engine", engine)
    database.create_tables()

    columns = {column["name"] for column in inspect(engine).get_columns("assessments")}
    assert {"attempt_number", "attempt_group_id", "question_source"}.issubset(columns)
    with engine.connect() as connection:
        record = connection.execute(text(
            "SELECT id, score, attempt_number, attempt_group_id, question_source FROM assessments WHERE id = 27"
        )).one()
    assert tuple(record) == (27, 9, 1, 27, "ai")
    index_names = {index["name"] for index in inspect(engine).get_indexes("assessments")}
    assert "uq_assessment_attempt_group_number" in index_names
    engine.dispose()
