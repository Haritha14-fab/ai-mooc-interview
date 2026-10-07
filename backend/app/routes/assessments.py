"""Assessment lifecycle endpoints. Scores, pass state, and locks are server-owned."""

from datetime import datetime, timezone
import json
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import Assessment, Answer, Question, User
from app.schemas.assessment import (
    AssessmentResponse,
    AssessmentResultQuestion,
    AssessmentResultResponse,
    CreateAssessmentRequest,
    DashboardStatsResponse,
    QuestionOption,
    QuestionResponse,
    SubmitAnswerRequest,
)
from app.services.ai_service import QuestionGenerationError, ai_service
from app.services.pdf_service import PDFService
from app.services.scoring_service import AIFeedbackService, ScoringService
from app.utils.constants import ASSESSMENT_STATUS, PASS_THRESHOLD, QUESTIONS_PER_ASSESSMENT

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/assessments", tags=["assessments"])


def _get_assessment(db: Session, user: User, assessment_id: int) -> Assessment:
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.user_id == user.id,
    ).first()
    if assessment is None:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment


def _validated_question_set(subject: str, difficulty: str) -> tuple[list[dict], str]:
    try:
        generated = ai_service.generate_questions(subject, difficulty)
        questions = ai_service._parse_questions(
            json.dumps({"questions": generated.get("questions")}, ensure_ascii=False)
        )
        source = generated.get("source", "ai")
        if source not in {"ai", "local"}:
            raise ValueError("Unknown question source")
        return questions, source
    except QuestionGenerationError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except (AttributeError, TypeError, ValueError, json.JSONDecodeError) as error:
        logger.warning("Question service returned an invalid assessment (%s)", type(error).__name__)
        raise HTTPException(
            status_code=502,
            detail="The question service returned an invalid assessment. Please try again.",
        ) from error


def _create_attempt(
    db: Session,
    user: User,
    subject: str,
    difficulty: str,
    attempt_number: int = 1,
    attempt_group_id: int | None = None,
) -> Assessment:
    question_data, question_source = _validated_question_set(subject, difficulty)
    assessment = Assessment(
        user_id=user.id,
        subject=subject,
        difficulty=difficulty,
        question_source=question_source,
        attempt_number=attempt_number,
        attempt_group_id=attempt_group_id,
        status=ASSESSMENT_STATUS["IN_PROGRESS"],
    )
    try:
        db.add(assessment)
        db.flush()
        if assessment.attempt_group_id is None:
            assessment.attempt_group_id = assessment.id

        for number, item in enumerate(question_data, start=1):
            question = Question(
                assessment_id=assessment.id,
                question_number=number,
                question_text=item["question"],
                option_a=item["options"]["A"],
                option_b=item["options"]["B"],
                option_c=item["options"]["C"],
                option_d=item["options"]["D"],
                correct_answer=item["correct_answer"],
                explanation=item["explanation"],
            )
            db.add(question)
            db.flush()
            db.add(Answer(assessment_id=assessment.id, question_id=question.id))

        db.commit()
        db.refresh(assessment)
        return assessment
    except SQLAlchemyError as error:
        db.rollback()
        logger.exception("Could not persist a generated assessment")
        raise HTTPException(
            status_code=500,
            detail="The assessment could not be saved. Please try again.",
        ) from error


def _score_assessment(db: Session, assessment: Assessment, generate_feedback: bool = True) -> dict:
    questions = db.query(Question).filter(
        Question.assessment_id == assessment.id
    ).order_by(Question.question_number).all()
    if len(questions) != QUESTIONS_PER_ASSESSMENT:
        raise HTTPException(
            status_code=409,
            detail="This assessment does not contain a complete question set and cannot be scored.",
        )

    answers = db.query(Answer).filter(Answer.assessment_id == assessment.id).all()
    answer_by_question = {answer.question_id: answer for answer in answers}
    scoring_result = ScoringService.evaluate_answers(
        [
            {"question_id": question_id, "user_answer": answer.user_answer}
            for question_id, answer in answer_by_question.items()
        ],
        [
            {"id": question.id, "correct_answer": question.correct_answer}
            for question in questions
        ],
    )

    result_by_question = {result["id"]: result for result in scoring_result["question_results"]}
    for question_id, answer in answer_by_question.items():
        answer.is_correct = 1 if result_by_question[question_id]["is_correct"] else 0

    assessment.correct_count = scoring_result["correct_count"]
    assessment.wrong_count = scoring_result["wrong_count"]
    assessment.unanswered_count = scoring_result["unanswered_count"]
    assessment.score = scoring_result["score"]
    assessment.percentage = scoring_result["percentage"]
    assessment.performance = ScoringService.get_performance_level(scoring_result["percentage"])
    assessment.status = ASSESSMENT_STATUS["SUBMITTED"]
    assessment.submitted_at = datetime.now(timezone.utc)

    if generate_feedback:
        feedback_input = {
            "question_results": [
                {
                    **result_by_question[question.id],
                    "question_text": question.question_text,
                }
                for question in questions
            ],
            **scoring_result,
        }
        assessment.ai_feedback = AIFeedbackService(ai_service).generate_feedback(
            subject=assessment.subject,
            difficulty=assessment.difficulty,
            correct_count=scoring_result["correct_count"],
            wrong_count=scoring_result["wrong_count"],
            total_questions=scoring_result["total_questions"],
            percentage=scoring_result["percentage"],
            question_results=feedback_input["question_results"],
            questions=questions,
        )
    else:
        assessment.ai_feedback = None

    return {"questions": questions, "answers": answer_by_question, "result": scoring_result}


def _result_response(assessment: Assessment, questions: list[Question], answers: dict[int, Answer]):
    passed = ScoringService.can_pass(assessment.percentage)
    result_questions = [
        AssessmentResultQuestion(
            id=question.id,
            question_number=question.question_number,
            question_text=question.question_text,
            options=QuestionOption(
                A=question.option_a,
                B=question.option_b,
                C=question.option_c,
                D=question.option_d,
            ),
            user_answer=answers[question.id].user_answer if question.id in answers else None,
            correct_answer=question.correct_answer,
            explanation=question.explanation,
            is_correct=(answers[question.id].is_correct == 1) if question.id in answers else False,
        )
        for question in questions
    ]
    return AssessmentResultResponse(
        id=assessment.id,
        subject=assessment.subject,
        difficulty=assessment.difficulty,
        attempt_number=assessment.attempt_number,
        status=assessment.status,
        created_at=assessment.created_at,
        submitted_at=assessment.submitted_at,
        final_submitted_at=assessment.final_submitted_at,
        total_questions=len(questions),
        correct_count=assessment.correct_count,
        wrong_count=assessment.wrong_count,
        unanswered_count=assessment.unanswered_count,
        score=assessment.score or 0,
        percentage=assessment.percentage or 0,
        performance=assessment.performance or "Not evaluated",
        questions=result_questions,
        ai_feedback=assessment.ai_feedback,
        can_retake=assessment.status != ASSESSMENT_STATUS["FINAL_SUBMITTED"],
        can_modify=assessment.status != ASSESSMENT_STATUS["FINAL_SUBMITTED"],
        passed=passed,
    )


@router.post("/", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
def create_assessment(
    request: CreateAssessmentRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    assessment = _create_attempt(db, user, request.subject, request.difficulty)
    return AssessmentResponse.model_validate(assessment)


@router.get("/", response_model=dict)
def list_assessments(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    assessments = db.query(Assessment).filter(
        Assessment.user_id == user.id
    ).order_by(Assessment.created_at.desc(), Assessment.id.desc()).all()
    return {
        "assessments": [AssessmentResponse.model_validate(item) for item in assessments],
        "count": len(assessments),
    }


@router.get("/stats/dashboard", response_model=DashboardStatsResponse)
def get_dashboard_stats(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    assessments = db.query(Assessment).filter(Assessment.user_id == user.id).all()
    completed = [
        item for item in assessments
        if item.status in {ASSESSMENT_STATUS["SUBMITTED"], ASSESSMENT_STATUS["FINAL_SUBMITTED"]}
    ]
    passed = [item for item in completed if ScoringService.can_pass(item.percentage)]
    scores = [item.score for item in completed if item.score is not None]
    return DashboardStatsResponse(
        total_assessments=len(assessments),
        completed_assessments=len(completed),
        average_score=sum(scores) / len(scores) if scores else 0,
        best_score=max(scores) if scores else 0,
        passed_count=len(passed),
        failed_count=len(completed) - len(passed),
    )


@router.get("/{assessment_id}", response_model=AssessmentResponse)
def get_assessment(
    assessment_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AssessmentResponse.model_validate(_get_assessment(db, user, assessment_id))


@router.get("/{assessment_id}/questions")
def get_assessment_questions(
    assessment_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    assessment = _get_assessment(db, user, assessment_id)
    if assessment.status == ASSESSMENT_STATUS["FINAL_SUBMITTED"]:
        raise HTTPException(status_code=403, detail="This assessment is locked and cannot be modified")

    questions = db.query(Question).filter(
        Question.assessment_id == assessment.id
    ).order_by(Question.question_number).all()
    answers = db.query(Answer).filter(Answer.assessment_id == assessment.id).all()
    answer_map = {answer.question_id: answer.user_answer for answer in answers}
    return {
        "assessment_id": assessment.id,
        "subject": assessment.subject,
        "difficulty": assessment.difficulty,
        "question_source": assessment.question_source,
        "attempt_number": assessment.attempt_number,
        "status": assessment.status,
        "total_questions": len(questions),
        "questions": [
            {
                "question": QuestionResponse(
                    id=question.id,
                    question_number=question.question_number,
                    question_text=question.question_text,
                    options=QuestionOption(
                        A=question.option_a,
                        B=question.option_b,
                        C=question.option_c,
                        D=question.option_d,
                    ),
                ),
                "user_answer": answer_map.get(question.id),
            }
            for question in questions
        ],
    }


@router.post("/{assessment_id}/answers")
def submit_answer(
    assessment_id: int,
    request: SubmitAnswerRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    assessment = _get_assessment(db, user, assessment_id)
    if assessment.status == ASSESSMENT_STATUS["FINAL_SUBMITTED"]:
        raise HTTPException(status_code=403, detail="This assessment is locked and cannot be modified")

    answer = db.query(Answer).join(Question, Answer.question_id == Question.id).filter(
        Answer.assessment_id == assessment.id,
        Question.assessment_id == assessment.id,
        Answer.question_id == request.question_id,
    ).first()
    if answer is None:
        raise HTTPException(status_code=404, detail="Question not found in this assessment")

    answer.user_answer = request.user_answer
    answer.updated_at = datetime.now(timezone.utc)
    if assessment.status == ASSESSMENT_STATUS["SUBMITTED"]:
        # Keep the stored result in sync while answers are being edited.
        _score_assessment(db, assessment, generate_feedback=False)
    try:
        db.commit()
    except SQLAlchemyError as error:
        db.rollback()
        logger.exception("Could not save an assessment answer")
        raise HTTPException(status_code=500, detail="Your answer could not be saved") from error
    return {"status": "success", "message": "Answer saved"}


@router.post("/{assessment_id}/submit", response_model=AssessmentResultResponse)
def submit_assessment(
    assessment_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    assessment = _get_assessment(db, user, assessment_id)
    if assessment.status == ASSESSMENT_STATUS["FINAL_SUBMITTED"]:
        raise HTTPException(status_code=403, detail="This assessment is locked and cannot be resubmitted")

    result = _score_assessment(db, assessment)
    try:
        db.commit()
        db.refresh(assessment)
    except SQLAlchemyError as error:
        db.rollback()
        logger.exception("Could not submit assessment")
        raise HTTPException(status_code=500, detail="The assessment could not be submitted") from error
    return _result_response(assessment, result["questions"], result["answers"])


@router.get("/{assessment_id}/result", response_model=AssessmentResultResponse)
def get_assessment_result(
    assessment_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    assessment = _get_assessment(db, user, assessment_id)
    if assessment.status == ASSESSMENT_STATUS["IN_PROGRESS"] or assessment.score is None:
        raise HTTPException(status_code=409, detail="Submit this assessment to view its result")
    questions = db.query(Question).filter(
        Question.assessment_id == assessment.id
    ).order_by(Question.question_number).all()
    answers = {
        answer.question_id: answer
        for answer in db.query(Answer).filter(Answer.assessment_id == assessment.id).all()
    }
    return _result_response(assessment, questions, answers)


@router.post("/{assessment_id}/retake", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
def retake_assessment(
    assessment_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    assessment = _get_assessment(db, user, assessment_id)
    if assessment.status == ASSESSMENT_STATUS["FINAL_SUBMITTED"]:
        raise HTTPException(status_code=403, detail="A final submitted assessment cannot be retaken")
    if assessment.status != ASSESSMENT_STATUS["SUBMITTED"]:
        raise HTTPException(status_code=409, detail="Submit this attempt before starting a retake")

    group_id = assessment.attempt_group_id or assessment.id
    previous_attempt = db.query(func.max(Assessment.attempt_number)).filter(
        Assessment.user_id == user.id,
        Assessment.attempt_group_id == group_id,
    ).scalar() or assessment.attempt_number
    new_assessment = _create_attempt(
        db,
        user,
        assessment.subject,
        assessment.difficulty,
        attempt_number=previous_attempt + 1,
        attempt_group_id=group_id,
    )
    return AssessmentResponse.model_validate(new_assessment)


@router.post("/{assessment_id}/final-submit")
def final_submit_assessment(
    assessment_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    assessment = _get_assessment(db, user, assessment_id)
    if assessment.status == ASSESSMENT_STATUS["FINAL_SUBMITTED"]:
        raise HTTPException(status_code=403, detail="This assessment is already locked")
    if assessment.status != ASSESSMENT_STATUS["SUBMITTED"]:
        raise HTTPException(status_code=409, detail="Submit the assessment before final submission")
    if not ScoringService.can_pass(assessment.percentage):
        raise HTTPException(
            status_code=400,
            detail=f"A score greater than {PASS_THRESHOLD}% is required for final submission",
        )

    assessment.status = ASSESSMENT_STATUS["FINAL_SUBMITTED"]
    assessment.final_submitted_at = datetime.now(timezone.utc)
    try:
        db.commit()
    except SQLAlchemyError as error:
        db.rollback()
        logger.exception("Could not lock assessment")
        raise HTTPException(status_code=500, detail="The assessment could not be finalized") from error
    return {
        "status": "success",
        "message": "Assessment finalized and locked",
        "assessment_id": assessment.id,
        "final_submitted_at": assessment.final_submitted_at,
    }


@router.get("/{assessment_id}/pdf")
def download_pdf_report(
    assessment_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    assessment = _get_assessment(db, user, assessment_id)
    if assessment.status == ASSESSMENT_STATUS["IN_PROGRESS"] or assessment.score is None:
        raise HTTPException(
            status_code=409,
            detail="Submit this assessment before downloading its report",
        )

    questions = db.query(Question).filter(
        Question.assessment_id == assessment.id
    ).order_by(Question.question_number).all()
    answers = {
        answer.question_id: answer
        for answer in db.query(Answer).filter(Answer.assessment_id == assessment.id).all()
    }
    question_results = []
    for question in questions:
        answer = answers.get(question.id)
        answer_letter = answer.user_answer if answer else None
        options = {
            "A": question.option_a,
            "B": question.option_b,
            "C": question.option_c,
            "D": question.option_d,
        }
        question_results.append({
            "question_number": question.question_number,
            "question_text": question.question_text,
            "user_answer": answer_letter,
            "user_answer_text": options.get(answer_letter, "Not answered"),
            "correct_answer": question.correct_answer,
            "correct_answer_text": options[question.correct_answer],
            "explanation": question.explanation,
            "is_correct": bool(answer and answer.is_correct == 1),
        })

    passed = ScoringService.can_pass(assessment.percentage)
    assessment_data = {
        "assessment_id": assessment.id,
        "user_name": user.name,
        "user_email": user.email,
        "subject": assessment.subject,
        "difficulty": assessment.difficulty,
        "attempt_number": assessment.attempt_number,
        "status": "PASS" if passed else "RETAKE REQUIRED",
        "created_at": assessment.created_at,
        "submitted_at": assessment.submitted_at,
        "final_submitted_at": assessment.final_submitted_at,
        "total_questions": len(questions),
        "correct_count": assessment.correct_count,
        "wrong_count": assessment.wrong_count,
        "unanswered_count": assessment.unanswered_count,
        "score": assessment.score,
        "percentage": assessment.percentage,
        "performance": assessment.performance,
        "ai_feedback": assessment.ai_feedback,
    }
    try:
        pdf_buffer = PDFService.generate_report(assessment_data, question_results)
    except Exception as error:
        logger.exception("Could not generate the assessment PDF")
        raise HTTPException(
            status_code=500,
            detail="The PDF report could not be generated. Please try again.",
        ) from error
    return StreamingResponse(
        iter([pdf_buffer.getvalue()]),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=assessment_{assessment.id}_report.pdf"},
    )
