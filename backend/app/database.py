"""Database configuration, session management, and small SQLite-safe migrations."""

from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

if settings.DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def enable_sqlite_foreign_keys(connection, _record):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Get database session dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create tables and add the attempt fields to databases from earlier versions."""
    # Import models here so metadata is complete even when this helper is used directly.
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)

    assessment_columns = {
        column["name"] for column in inspect(engine).get_columns("assessments")
    }
    with engine.begin() as connection:
        if "attempt_number" not in assessment_columns:
            connection.execute(text(
                "ALTER TABLE assessments ADD COLUMN attempt_number INTEGER NOT NULL DEFAULT 1"
            ))
        if "attempt_group_id" not in assessment_columns:
            connection.execute(text(
                "ALTER TABLE assessments ADD COLUMN attempt_group_id INTEGER"
            ))
        if "question_source" not in assessment_columns:
            connection.execute(text(
                "ALTER TABLE assessments ADD COLUMN question_source VARCHAR(20) NOT NULL DEFAULT 'ai'"
            ))
        connection.execute(text(
            "UPDATE assessments SET attempt_group_id = id WHERE attempt_group_id IS NULL"
        ))
        connection.execute(text(
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_assessment_attempt_group_number "
            "ON assessments (user_id, attempt_group_id, attempt_number)"
        ))
        connection.execute(text(
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_questions_assessment_number "
            "ON questions (assessment_id, question_number)"
        ))
        connection.execute(text(
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_answers_question ON answers (question_id)"
        ))
