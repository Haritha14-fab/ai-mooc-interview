"""Subject routes"""
from fastapi import APIRouter
from app.utils.constants import SUBJECTS, DIFFICULTY_LEVELS

router = APIRouter(prefix="/api/subjects", tags=["subjects"])


@router.get("/")
def get_subjects():
    """Get all available subjects"""
    return {
        "subjects": SUBJECTS,
        "count": len(SUBJECTS)
    }


@router.get("/difficulties")
def get_difficulties():
    """Get all available difficulty levels"""
    return {
        "difficulties": DIFFICULTY_LEVELS,
        "count": len(DIFFICULTY_LEVELS)
    }
