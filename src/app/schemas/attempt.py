from pydantic import BaseModel
from datetime import datetime

class AnswerSubmission(BaseModel):
    question_id: int
    selected_answer: str


class QuizSubmission(BaseModel):
    answers: list[AnswerSubmission]


class QuizResult(BaseModel):
    score: int
    total_questions: int
    percentage: float


class AttemptResponse(BaseModel):
    quiz_id: int
    topic: str
    score: int
    total_questions: int
    attempted_at: datetime