"""Assessment request and response schemas."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.utils.constants import DIFFICULTY_LEVELS, SUBJECTS

AnswerLetter = Literal["A", "B", "C", "D"]


class QuestionOption(BaseModel):
    model_config = ConfigDict(extra="forbid")

    A: str
    B: str
    C: str
    D: str


class QuestionResponse(BaseModel):
    """Question shape returned while the user is taking an assessment."""

    id: int
    question_number: int
    question_text: str
    options: QuestionOption


class CreateAssessmentRequest(BaseModel):
    subject: str = Field(min_length=1, max_length=100)
    difficulty: str = Field(min_length=1, max_length=50)

    @field_validator("subject")
    @classmethod
    def validate_subject(cls, value: str) -> str:
        value = value.strip()
        if value not in SUBJECTS:
            raise ValueError("Choose a supported subject")
        return value

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, value: str) -> str:
        value = value.strip()
        if value not in DIFFICULTY_LEVELS:
            raise ValueError("Choose a supported difficulty level")
        return value


class AssessmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    subject: str
    difficulty: str
    question_source: str
    attempt_number: int
    status: str
    score: int | None
    correct_count: int
    wrong_count: int
    unanswered_count: int
    percentage: float | None
    performance: str | None
    created_at: datetime
    submitted_at: datetime | None
    final_submitted_at: datetime | None


class SubmitAnswerRequest(BaseModel):
    question_id: int = Field(gt=0)
    user_answer: AnswerLetter | None


class AssessmentResultQuestion(BaseModel):
    id: int
    question_number: int
    question_text: str
    options: QuestionOption
    user_answer: AnswerLetter | None
    correct_answer: AnswerLetter
    explanation: str
    is_correct: bool


class AssessmentResultResponse(BaseModel):
    id: int
    subject: str
    difficulty: str
    attempt_number: int
    status: str
    created_at: datetime
    submitted_at: datetime | None
    final_submitted_at: datetime | None
    total_questions: int
    correct_count: int
    wrong_count: int
    unanswered_count: int
    score: int
    percentage: float
    performance: str
    questions: list[AssessmentResultQuestion]
    ai_feedback: str | None
    can_retake: bool
    can_modify: bool
    passed: bool


class DashboardStatsResponse(BaseModel):
    total_assessments: int
    completed_assessments: int
    average_score: float
    best_score: int
    passed_count: int
    failed_count: int
