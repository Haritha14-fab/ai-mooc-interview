"""Assessment models"""
from sqlalchemy import Column, Float, ForeignKey, Index, Integer, String, Text, DateTime
from datetime import datetime, timezone
from app.database import Base


class Assessment(Base):
    """Assessment model for storing assessment information"""
    __tablename__ = "assessments"
    __table_args__ = (
        Index(
            "uq_assessment_attempt_group_number",
            "user_id", "attempt_group_id", "attempt_number",
            unique=True,
        ),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    attempt_group_id = Column(Integer, nullable=True, index=True)
    attempt_number = Column(Integer, default=1, nullable=False)
    subject = Column(String(100), nullable=False)
    difficulty = Column(String(50), nullable=False)
    question_source = Column(String(20), default="ai", nullable=False)
    status = Column(String(50), default="in_progress")  # in_progress, submitted, final_submitted
    score = Column(Integer, nullable=True)
    correct_count = Column(Integer, default=0)
    wrong_count = Column(Integer, default=0)
    unanswered_count = Column(Integer, default=0)
    percentage = Column(Float, nullable=True)
    performance = Column(String(50), nullable=True)  # Excellent, Very Good, Good, etc.
    ai_feedback = Column(Text, nullable=True)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    submitted_at = Column(DateTime, nullable=True)
    final_submitted_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Assessment(id={self.id}, user_id={self.user_id}, subject={self.subject})>"


class Question(Base):
    """Question model for storing MCQ questions"""
    __tablename__ = "questions"
    __table_args__ = (
        Index("uq_questions_assessment_number", "assessment_id", "question_number", unique=True),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    question_number = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=False)
    option_a = Column(Text, nullable=False)
    option_b = Column(Text, nullable=False)
    option_c = Column(Text, nullable=False)
    option_d = Column(Text, nullable=False)
    correct_answer = Column(String(1), nullable=False)  # A, B, C, or D
    explanation = Column(Text, nullable=False)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    def __repr__(self):
        return f"<Question(id={self.id}, assessment_id={self.assessment_id})>"


class Answer(Base):
    """Answer model for storing user answers"""
    __tablename__ = "answers"
    __table_args__ = (
        Index("uq_answers_question", "question_id", unique=True),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    user_answer = Column(String(1), nullable=True)  # A, B, C, D, or null if unanswered
    is_correct = Column(Integer, default=-1, nullable=False)  # -1: not evaluated, 0: wrong, 1: correct
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    def __repr__(self):
        return f"<Answer(id={self.id}, assessment_id={self.assessment_id})>"
