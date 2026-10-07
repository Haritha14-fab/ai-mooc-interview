"""End-to-end API coverage for scoring, retakes, ownership, locking, and reports."""

from io import BytesIO

from pypdf import PdfReader


def start_assessment(client, headers, subject="Python", difficulty="Intermediate"):
    response = client.post(
        "/api/assessments/",
        headers=headers,
        json={"subject": subject, "difficulty": difficulty},
    )
    assert response.status_code == 201, response.text
    return response.json()


def submit_answers(client, headers, assessment_id, correct_count):
    response = client.get(f"/api/assessments/{assessment_id}/questions", headers=headers)
    assert response.status_code == 200, response.text
    rows = response.json()["questions"]
    for index, row in enumerate(rows):
        question = row["question"]
        answer = "A" if index < correct_count else "B"
        saved = client.post(
            f"/api/assessments/{assessment_id}/answers",
            headers=headers,
            json={"question_id": question["id"], "user_answer": answer},
        )
        assert saved.status_code == 200, saved.text
    return rows


def test_exact_question_shape_and_no_answers_before_submission(client, register_user):
    headers, _ = register_user()
    assessment = start_assessment(client, headers)
    response = client.get(f"/api/assessments/{assessment['id']}/questions", headers=headers)

    assert response.status_code == 200
    assert response.json()["question_source"] == "ai"
    rows = response.json()["questions"]
    assert len(rows) == 10
    for row in rows:
        question = row["question"]
        assert set(question["options"]) == {"A", "B", "C", "D"}
        assert "correct_answer" not in question
        assert "explanation" not in question


def test_local_question_source_is_exposed_without_revealing_answers(client, register_user, monkeypatch):
    from app.services.ai_service import ai_service
    from app.services.question_bank import generate_local_questions

    headers, _ = register_user()
    monkeypatch.setattr(
        ai_service,
        "generate_questions",
        lambda subject, difficulty: {
            "subject": subject,
            "difficulty": difficulty,
            "questions": generate_local_questions(subject, difficulty),
            "source": "local",
        },
    )
    assessment = start_assessment(client, headers)
    assert assessment["question_source"] == "local"

    response = client.get(f"/api/assessments/{assessment['id']}/questions", headers=headers)
    assert response.status_code == 200
    assert response.json()["question_source"] == "local"
    assert len(response.json()["questions"]) == 10
    assert all("correct_answer" not in row["question"] for row in response.json()["questions"])


def test_eighty_percent_fails_and_retake_preserves_both_attempts(client, register_user):
    headers, _ = register_user()
    first = start_assessment(client, headers)
    submit_answers(client, headers, first["id"], correct_count=8)

    result = client.post(f"/api/assessments/{first['id']}/submit", headers=headers).json()
    assert result["score"] == 8
    assert result["percentage"] == 80
    assert result["passed"] is False
    assert result["status"] == "submitted"
    assert result["correct_count"] == 8
    assert result["wrong_count"] == 2
    assert result["unanswered_count"] == 0
    assert client.post(f"/api/assessments/{first['id']}/final-submit", headers=headers).status_code == 400

    second_response = client.post(f"/api/assessments/{first['id']}/retake", headers=headers)
    assert second_response.status_code == 201, second_response.text
    second = second_response.json()
    assert second["id"] != first["id"]
    assert second["attempt_number"] == 2
    assert second["status"] == "in_progress"
    first_questions = client.get(f"/api/assessments/{first['id']}/questions", headers=headers).json()["questions"]
    second_questions = client.get(f"/api/assessments/{second['id']}/questions", headers=headers).json()["questions"]
    assert {row["question"]["id"] for row in first_questions}.isdisjoint(
        {row["question"]["id"] for row in second_questions}
    )

    history = client.get("/api/assessments/", headers=headers).json()["assessments"]
    attempts = {item["id"]: item for item in history}
    assert attempts[first["id"]]["status"] == "submitted"
    assert attempts[second["id"]]["attempt_number"] == 2
    stats = client.get("/api/assessments/stats/dashboard", headers=headers).json()
    assert stats["total_assessments"] == 2
    assert stats["completed_assessments"] == 1
    assert stats["failed_count"] == 1


def test_ninety_percent_passes_and_final_submission_locks_every_mutation(client, register_user):
    headers, _ = register_user()
    assessment = start_assessment(client, headers)
    rows = submit_answers(client, headers, assessment["id"], correct_count=9)

    result_response = client.post(f"/api/assessments/{assessment['id']}/submit", headers=headers)
    assert result_response.status_code == 200, result_response.text
    result = result_response.json()
    assert result["score"] == 9
    assert result["percentage"] == 90
    assert result["passed"] is True

    finalized = client.post(f"/api/assessments/{assessment['id']}/final-submit", headers=headers)
    assert finalized.status_code == 200, finalized.text
    assert finalized.json()["final_submitted_at"]

    locked_result = client.get(f"/api/assessments/{assessment['id']}/result", headers=headers).json()
    assert locked_result["status"] == "final_submitted"
    assert locked_result["can_modify"] is False
    assert locked_result["can_retake"] is False

    question_id = rows[0]["question"]["id"]
    assert client.post(
        f"/api/assessments/{assessment['id']}/answers",
        headers=headers,
        json={"question_id": question_id, "user_answer": "B"},
    ).status_code == 403
    assert client.post(f"/api/assessments/{assessment['id']}/submit", headers=headers).status_code == 403
    assert client.post(f"/api/assessments/{assessment['id']}/retake", headers=headers).status_code == 403
    assert client.post(f"/api/assessments/{assessment['id']}/final-submit", headers=headers).status_code == 403

    pdf = client.get(f"/api/assessments/{assessment['id']}/pdf", headers=headers)
    assert pdf.status_code == 200
    assert pdf.content.startswith(b"%PDF")
    reader = PdfReader(BytesIO(pdf.content))
    assert len(reader.pages) >= 1
    report_text = "\n".join(page.extract_text() or "" for page in reader.pages)
    assert "Candidate User" in report_text
    assert "Assessment ID" in report_text
    assert "PASS" in report_text

    new_assessment = start_assessment(client, headers, subject="SQL", difficulty="Advanced")
    assert new_assessment["attempt_number"] == 1
    assert new_assessment["id"] != assessment["id"]


def test_authentication_authorization_and_answer_validation(client, register_user):
    headers, _ = register_user("owner@example.com", "Owner")
    stranger_headers, _ = register_user("stranger@example.com", "Stranger")
    assessment = start_assessment(client, headers)
    question = client.get(f"/api/assessments/{assessment['id']}/questions", headers=headers).json()["questions"][0]["question"]

    assert client.get(f"/api/assessments/{assessment['id']}", headers=stranger_headers).status_code == 404
    assert client.get(f"/api/assessments/{assessment['id']}/pdf", headers=stranger_headers).status_code == 404
    assert client.get("/api/auth/me", params={"token": headers["Authorization"].split()[1]}).status_code == 401
    invalid = client.post(
        f"/api/assessments/{assessment['id']}/answers",
        headers=headers,
        json={"question_id": question["id"], "user_answer": "Z"},
    )
    assert invalid.status_code == 422
    assert client.post(
        f"/api/assessments/{assessment['id']}/answers",
        headers=headers,
        json={"question_id": 99999, "user_answer": "A"},
    ).status_code == 404
    assert client.get("/api/assessments/99999", headers=headers).status_code == 404


def test_login_returns_a_bearer_token_and_profile(client, register_user):
    headers, user = register_user("login@example.com", "Login Candidate")
    login = client.post(
        "/api/auth/login",
        json={"email": "login@example.com", "password": "SufficientPass9!"},
    )
    assert login.status_code == 200
    assert login.json()["token_type"] == "bearer"
    profile = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {login.json()['access_token']}"},
    )
    assert profile.status_code == 200
    assert profile.json()["id"] == user["id"]
    assert client.post(
        "/api/auth/login",
        json={"email": "login@example.com", "password": "wrong-password"},
    ).status_code == 401


def test_failed_question_generation_does_not_leave_an_assessment(client, register_user, monkeypatch):
    from app.services.ai_service import QuestionGenerationError, ai_service

    headers, _ = register_user()

    def unavailable(subject, difficulty):
        raise QuestionGenerationError("Question service unavailable")

    monkeypatch.setattr(ai_service, "generate_questions", unavailable)
    response = client.post(
        "/api/assessments/",
        headers=headers,
        json={"subject": "Python", "difficulty": "Advanced"},
    )
    assert response.status_code == 503
    assert client.get("/api/assessments/", headers=headers).json()["count"] == 0


def test_invalid_ai_question_set_is_rejected_without_persisting_partial_data(client, register_user, monkeypatch):
    from app.services.ai_service import ai_service

    headers, _ = register_user()
    monkeypatch.setattr(ai_service, "generate_questions", lambda *_: {"questions": []})
    response = client.post(
        "/api/assessments/",
        headers=headers,
        json={"subject": "Python", "difficulty": "Advanced"},
    )
    assert response.status_code == 502
    assert client.get("/api/assessments/", headers=headers).json()["count"] == 0


def test_modified_answer_recalculates_result(client, register_user):
    headers, _ = register_user()
    assessment = start_assessment(client, headers)
    rows = submit_answers(client, headers, assessment["id"], correct_count=8)
    first_result = client.post(f"/api/assessments/{assessment['id']}/submit", headers=headers).json()
    assert first_result["percentage"] == 80

    modified = client.post(
        f"/api/assessments/{assessment['id']}/answers",
        headers=headers,
        json={"question_id": rows[8]["question"]["id"], "user_answer": "A"},
    )
    assert modified.status_code == 200
    updated = client.get(f"/api/assessments/{assessment['id']}/result", headers=headers).json()
    assert updated["percentage"] == 90
    assert updated["passed"] is True


def test_unanswered_questions_are_counted_as_unanswered(client, register_user):
    headers, _ = register_user()
    assessment = start_assessment(client, headers)
    result = client.post(f"/api/assessments/{assessment['id']}/submit", headers=headers).json()
    assert result["score"] == 0
    assert result["percentage"] == 0
    assert result["wrong_count"] == 0
    assert result["unanswered_count"] == 10


def test_pdf_wraps_long_text_and_escapes_markup(client, register_user, monkeypatch):
    from app.services.ai_service import ai_service

    headers, _ = register_user()
    long_text = ("A long technical prompt with <tag> and & characters. " * 22).strip()
    questions = [
        {
            "question": f"{number}. {long_text}",
            "options": {"A": "Correct & safe", "B": "Second", "C": "Third", "D": "Fourth"},
            "correct_answer": "A",
            "explanation": long_text,
        }
        for number in range(1, 11)
    ]
    monkeypatch.setattr(ai_service, "generate_questions", lambda *_: {"questions": questions})
    assessment = start_assessment(client, headers)
    submit_answers(client, headers, assessment["id"], correct_count=9)
    client.post(f"/api/assessments/{assessment['id']}/submit", headers=headers)
    pdf = client.get(f"/api/assessments/{assessment['id']}/pdf", headers=headers)

    assert pdf.status_code == 200
    reader = PdfReader(BytesIO(pdf.content))
    assert len(reader.pages) > 1
    report_text = "\n".join(page.extract_text() or "" for page in reader.pages)
    assert "A long technical prompt" in report_text


def test_login_rate_limit_returns_retry_after(client):
    payload = {"email": "missing@example.com", "password": "SufficientPass9!"}
    for _ in range(10):
        assert client.post("/api/auth/login", json=payload).status_code == 401
    limited = client.post("/api/auth/login", json=payload)
    assert limited.status_code == 429
    assert limited.headers["Retry-After"] == "60"
