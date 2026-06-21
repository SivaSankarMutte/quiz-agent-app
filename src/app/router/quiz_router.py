from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User

from app.schemas.quiz import QuizRequest

from app.services.quiz_service import QuizService

from app.auth.dependencies import get_current_user

from app.schemas.attempt import (
    QuizSubmission
)

from app.auth.dependencies import (
    get_current_user
)

from app.schemas.attempt import AttemptResponse


router = APIRouter(
    prefix="/quiz",
    tags=["Quiz"]
)

quiz_service = QuizService()


@router.post("/")
def create_quiz(
    request: QuizRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return quiz_service.get_or_create_quiz(
        db=db,
        topic=request.topic,
        no_of_questions=request.no_of_questions
    )


@router.get("/all")
def get_all_quizzes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return quiz_service.get_all_quizzes(
        db=db,
        current_user_id=current_user.id
    )



@router.get("/{quiz_id}/answers")
def get_answers(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = quiz_service.get_answers(
        db=db,
        quiz_id=quiz_id
    )

    if not result:
        return {
            "message": "Quiz not found"
        }

    return result


@router.post("/{quiz_id}/submit")
def submit_quiz(
    quiz_id: int,
    submission: QuizSubmission,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    result = quiz_service.submit_quiz(
        db=db,
        quiz_id=quiz_id,
        user_id=current_user.id,
        answers=submission.answers
    )

    if not result:
        return {
            "message": "Quiz not found"
        }

    return result

@router.get("/{quiz_id}/leaderboard")
def get_leaderboard(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    return quiz_service.get_leaderboard(
        db=db,
        quiz_id=quiz_id
    )


@router.get(
    "/my-attempts",
    response_model=list[AttemptResponse]
)
def get_my_attempts(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):
    
    return quiz_service.get_user_attempts(
        db=db,
        user_id=current_user.id
    )


@router.get("/{quiz_id}")
def get_quiz(
    quiz_id: int,
    db: Session = Depends(get_db)
):

    result = quiz_service.get_quiz(
        db=db,
        quiz_id=quiz_id
    )

    if not result:
        return {
            "message": "Quiz not found"
        }

    return result


