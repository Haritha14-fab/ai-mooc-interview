"""Validated question and feedback generation for the configured AI provider."""

import json
import logging
import re
from typing import Any

from app.config import settings
from app.services.question_bank import generate_local_questions

logger = logging.getLogger(__name__)


class QuestionGenerationError(RuntimeError):
    """Raised when an assessment question set cannot be generated safely."""


class AIService:
    """Small provider adapter for OpenAI and Anthropic."""

    def __init__(self):
        self.provider = settings.AI_PROVIDER.lower()

    @property
    def api_key(self) -> str | None:
        if self.provider == "openai":
            return settings.OPENAI_API_KEY
        if self.provider == "claude":
            return settings.CLAUDE_API_KEY
        return None

    @property
    def has_usable_api_key(self) -> bool:
        key = self.api_key
        if not key or not key.strip():
            return False
        placeholder_markers = ("your", "placeholder", "example", "changeme")
        return not any(marker in key.casefold() for marker in placeholder_markers)

    def generate_questions(self, subject: str, difficulty: str) -> dict[str, Any]:
        """Generate ten questions with AI, falling back to the built-in bank."""
        if not self.has_usable_api_key:
            return self._local_question_set(subject, difficulty, "no usable provider key")

        prompt = self._question_prompt(subject, difficulty)
        last_invalid_response = False
        for attempt in range(2):
            if attempt:
                prompt += (
                    "\nYour previous response was invalid. Return one valid JSON object with exactly "
                    "10 distinct questions, each with exactly four non-empty options and one valid answer."
                )
            try:
                content = self._complete(
                    system="You create technically accurate, unambiguous interview assessments. Follow the requested level exactly.",
                    prompt=prompt,
                    max_tokens=5000,
                )
            except Exception as error:
                logger.warning("Question provider request failed (%s)", type(error).__name__)
                return self._local_question_set(
                    subject, difficulty, self._question_provider_error_message(error)
                )

            try:
                questions = self._parse_questions(content)
                return {
                    "subject": subject,
                    "difficulty": difficulty,
                    "questions": questions,
                    "source": "ai",
                }
            except (ValueError, json.JSONDecodeError):
                last_invalid_response = True

        if last_invalid_response:
            return self._local_question_set(subject, difficulty, "invalid provider response")
        return self._local_question_set(subject, difficulty, "provider returned no questions")

    @staticmethod
    def _local_question_set(subject: str, difficulty: str, reason: str) -> dict[str, Any]:
        logger.info("Using built-in question bank (%s)", reason)
        return {
            "subject": subject,
            "difficulty": difficulty,
            "questions": generate_local_questions(subject, difficulty),
            "source": "local",
        }

    def _question_provider_error_message(self, error: Exception) -> str:
        """Give actionable setup guidance without exposing provider response details."""
        error_type = type(error).__name__
        key_name = "OPENAI_API_KEY" if self.provider == "openai" else "CLAUDE_API_KEY"

        if error_type == "AuthenticationError":
            return (
                f"The configured {self.provider.upper()} API key was rejected. "
                f"Set a valid {key_name} in backend/.env and restart the backend."
            )
        if error_type == "PermissionDeniedError":
            return (
                f"The configured {self.provider.upper()} key cannot use the selected model. "
                f"Check model access for {key_name} in backend/.env."
            )
        if error_type == "RateLimitError":
            return (
                f"The configured {self.provider.upper()} account has reached its usage limit. "
                "Check its quota or billing, then retry."
            )
        if error_type == "APIConnectionError":
            return (
                f"The backend cannot reach {self.provider.upper()}. Check its network/proxy access, "
                "then retry."
            )
        return "Question generation failed. Check the AI provider configuration and try again."

    def generate_feedback(self, subject: str, difficulty: str, result: dict) -> str | None:
        """Ask the provider for coaching feedback; scoring is never delegated to it."""
        if not self.has_usable_api_key:
            return None

        review = [
            {
                "question": item["question_text"],
                "answered_correctly": item["is_correct"],
            }
            for item in result["question_results"]
        ]
        prompt = (
            "Write concise, supportive learning feedback for this technical assessment. Include a brief "
            "overall summary, strengths, topics to review, and two practical next steps. Use plain text "
            "with short headings, no markdown markers, and no more than 120 words. Do not calculate or "
            "change the result. Use only the supplied facts.\n"
            f"Subject: {subject}\nDifficulty: {difficulty}\n"
            f"Score: {result['correct_count']}/{result['total_questions']} "
            f"({result['percentage']:.1f}%)\nQuestion review: {json.dumps(review, ensure_ascii=False)}"
        )
        try:
            content = self._complete(
                system="You are a concise technical learning coach.",
                prompt=prompt,
                max_tokens=700,
            ).strip()
            return content[:4000] or None
        except Exception as error:
            logger.info("AI feedback unavailable (%s)", type(error).__name__)
            return None

    @staticmethod
    def _question_prompt(subject: str, difficulty: str) -> str:
        return f"""Create exactly 10 interview-quality MCQs for:
Subject: {subject}
Difficulty: {difficulty}

Match the selected difficulty in every question. Use technically correct, clear questions with one defensible answer. Avoid duplicates, trick wording, and placeholder content. Include a short explanation of the correct answer. Return only a JSON object in this shape:
{{
  "questions": [
    {{
      "question": "Question text",
      "options": {{"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"}},
      "correct_answer": "A",
      "explanation": "Why A is correct"
    }}
  ]
}}
"""

    def _complete(self, system: str, prompt: str, max_tokens: int) -> str:
        if self.provider == "openai":
            from openai import OpenAI

            client = OpenAI(
                api_key=self.api_key,
                timeout=settings.AI_TIMEOUT_SECONDS,
                max_retries=1,
            )
            request = {
                "model": settings.OPENAI_MODEL,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.4,
                "max_tokens": max_tokens,
            }
            if "MCQs" in prompt:
                request["response_format"] = {"type": "json_object"}
            response = client.chat.completions.create(**request)
            content = response.choices[0].message.content
            if not content:
                raise ValueError("The provider returned an empty response")
            return content

        if self.provider == "claude":
            from anthropic import Anthropic

            client = Anthropic(
                api_key=self.api_key,
                timeout=settings.AI_TIMEOUT_SECONDS,
                max_retries=1,
            )
            response = client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": prompt}],
            )
            text_blocks = [block.text for block in response.content if getattr(block, "type", None) == "text"]
            if not text_blocks:
                raise ValueError("The provider returned an empty response")
            return "\n".join(text_blocks)

        raise ValueError("Unsupported AI provider")

    @classmethod
    def _parse_questions(cls, content: str) -> list[dict[str, Any]]:
        start = content.find("{")
        if start < 0:
            raise ValueError("No JSON object found")
        data, _ = json.JSONDecoder().raw_decode(content[start:])
        if not isinstance(data, dict) or not isinstance(data.get("questions"), list):
            raise ValueError("Missing questions array")
        questions = data["questions"]
        if len(questions) != 10:
            raise ValueError("Expected exactly ten questions")

        validated = []
        seen = set()
        for question in questions:
            if not isinstance(question, dict):
                raise ValueError("Question must be an object")
            prompt = cls._required_text(question.get("question"), 2000)
            options = question.get("options")
            if not isinstance(options, dict) or set(options) != {"A", "B", "C", "D"}:
                raise ValueError("Each question must have exactly four options")
            options = {key: cls._required_text(options[key], 1000) for key in "ABCD"}
            answer = question.get("correct_answer")
            if answer not in {"A", "B", "C", "D"}:
                raise ValueError("Correct answer must be A, B, C, or D")
            explanation = cls._required_text(question.get("explanation"), 3000)

            normalized = re.sub(r"\W+", " ", prompt.casefold()).strip()
            if normalized in seen:
                raise ValueError("Duplicate question")
            seen.add(normalized)
            if len({value.casefold().strip() for value in options.values()}) != 4:
                raise ValueError("Options must be distinct")
            validated.append({
                "question": prompt,
                "options": options,
                "correct_answer": answer,
                "explanation": explanation,
            })
        return validated

    @staticmethod
    def _required_text(value: Any, max_length: int) -> str:
        if not isinstance(value, str):
            raise ValueError("Expected non-empty text")
        value = value.strip()
        if not value or len(value) > max_length:
            raise ValueError("Text is empty or too long")
        return value


ai_service = AIService()
