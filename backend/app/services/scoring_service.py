"""Assessment scoring service"""
from typing import Dict, List

from app.utils.constants import PASS_THRESHOLD


class ScoringService:
    """Service for scoring assessments and evaluating answers"""
    
    @staticmethod
    def evaluate_answers(
        answers: List[Dict],
        questions_with_answers: List[Dict]
    ) -> Dict:
        """Evaluate user answers against correct answers
        
        Args:
            answers: List of user answers with format [{question_id, user_answer}, ...]
            questions_with_answers: List of questions with correct answers
        
        Returns:
            Dictionary with scoring results
        """
        correct_count = 0
        wrong_count = 0
        unanswered_count = 0
        question_results = []
        
        # Create a map of question_id to correct answer for quick lookup
        answer_map = {
            answer["question_id"]: answer.get("user_answer")
            for answer in answers
        }
        
        for question in questions_with_answers:
            question_id = question["id"]
            correct_answer = question["correct_answer"]
            user_answer = answer_map.get(question_id)
            
            if user_answer is None:
                is_correct = False
                unanswered_count += 1
            elif user_answer == correct_answer:
                is_correct = True
                correct_count += 1
            else:
                is_correct = False
                wrong_count += 1
            
            question_results.append({
                "id": question_id,
                "is_correct": is_correct,
                "user_answer": user_answer,
                "correct_answer": correct_answer
            })
        
        # Calculate score and percentage
        total_questions = len(questions_with_answers)
        score = correct_count
        percentage = (correct_count / total_questions * 100) if total_questions > 0 else 0
        
        return {
            "correct_count": correct_count,
            "wrong_count": wrong_count,
            "unanswered_count": unanswered_count,
            "score": score,
            "percentage": percentage,
            "question_results": question_results,
            "total_questions": total_questions
        }
    
    @staticmethod
    def get_performance_level(percentage: float) -> str:
        """Get performance level based on percentage"""
        if percentage >= 90:
            return "Excellent"
        elif percentage > PASS_THRESHOLD:
            return "Very Good"
        elif percentage >= 60:
            return "Good"
        elif percentage >= 40:
            return "Needs Improvement"
        else:
            return "Poor"
    
    @staticmethod
    def can_pass(percentage: float) -> bool:
        """Check if assessment is passed (must be > 80%)"""
        return percentage is not None and percentage > PASS_THRESHOLD
    
    @staticmethod
    def needs_retake(percentage: float) -> bool:
        """Check if assessment needs retake (score <= 80%)"""
        return percentage is None or percentage <= PASS_THRESHOLD


class AIFeedbackService:
    """Service for generating AI feedback on performance"""
    
    def __init__(self, ai_service):
        self.ai_service = ai_service
    
    def generate_feedback(
        self,
        subject: str,
        difficulty: str,
        correct_count: int,
        wrong_count: int,
        total_questions: int,
        percentage: float,
        question_results: List[Dict],
        questions: List[Dict]
    ) -> str:
        """Generate personalized AI feedback on assessment performance"""
        
        result = {
            "correct_count": correct_count,
            "wrong_count": wrong_count,
            "total_questions": total_questions,
            "percentage": percentage,
            "question_results": question_results,
        }
        feedback = self.ai_service.generate_feedback(subject, difficulty, result)
        if feedback:
            return feedback

        missed = sum(1 for question in question_results if not question["is_correct"])
        if missed == 0:
            focus = "Keep building on this strong result with more advanced practice."
        else:
            focus = (
                f"Review the explanations for the {missed} missed question(s), then practice "
                f"the underlying {subject} concepts at the {difficulty.lower()} level."
            )
        return (
            f"Performance analysis\n\n"
            f"You answered {correct_count} of {total_questions} questions correctly ({percentage:.1f}%). "
            f"{focus}\n\n"
            "Next steps\n"
            "• Revisit the question explanations.\n"
            "• Practice a short set of related problems before your next attempt."
        )
