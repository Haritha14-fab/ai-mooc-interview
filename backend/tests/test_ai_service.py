import pytest

from app.config import settings
from app.services.ai_service import AIService
from app.utils.constants import DIFFICULTY_LEVELS, SUBJECTS


class AuthenticationError(Exception):
    pass


class APIConnectionError(Exception):
    pass


@pytest.mark.parametrize(
    ("provider_error", "expected_message"),
    [
        (AuthenticationError("provider response includes sensitive details"), "OPENAI_API_KEY"),
        (APIConnectionError("network details"), "cannot reach OPENAI"),
    ],
)
def test_question_generation_reports_actionable_provider_failures(
    monkeypatch, provider_error, expected_message
):
    monkeypatch.setattr(settings, "AI_PROVIDER", "openai")
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "test-only-key")
    service = AIService()

    def fail_request(**_kwargs):
        raise provider_error

    monkeypatch.setattr(service, "_complete", fail_request)

    generated = service.generate_questions("Python", "Basic")

    assert expected_message in service._question_provider_error_message(provider_error)
    assert generated["source"] == "local"
    assert len(generated["questions"]) == 10
    assert "test-only-key" not in repr(generated)
    assert "sensitive details" not in repr(generated)


def test_question_generation_rejects_placeholder_key_without_provider_call(monkeypatch):
    monkeypatch.setattr(settings, "AI_PROVIDER", "openai")
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-your-openai-key-here")
    service = AIService()
    monkeypatch.setattr(
        service,
        "_complete",
        lambda **_kwargs: pytest.fail("A placeholder key must not be sent to the provider"),
    )

    generated = service.generate_questions("Python", "Basic")
    assert generated["source"] == "local"
    assert len(generated["questions"]) == 10


@pytest.mark.parametrize("subject", SUBJECTS)
@pytest.mark.parametrize("difficulty", DIFFICULTY_LEVELS)
def test_builtin_question_bank_returns_ten_distinct_valid_questions(subject, difficulty):
    from app.services.question_bank import generate_local_questions

    questions = generate_local_questions(subject, difficulty)

    assert len(questions) == 10
    assert len({question["question"] for question in questions}) == 10
    for question in questions:
        assert set(question["options"]) == {"A", "B", "C", "D"}
        assert question["correct_answer"] in {"A", "B", "C", "D"}
        assert len(set(question["options"].values())) == 4
        assert question["explanation"]
