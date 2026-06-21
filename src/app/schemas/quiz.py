from datetime import datetime

from pydantic import BaseModel
from typing import List, Literal

from pydantic import Field



class QuizRequest(BaseModel):
    topic: str = Field(
        min_length=2,
        max_length=100
    )
    no_of_questions: int = Field(
        ge=1,
        default=5
    )


class AgentQuestion(BaseModel):
    question_text: str

    option_a: str
    option_b: str
    option_c: str
    option_d: str

    correct_answer: Literal["A", "B", "C", "D"]

    explanation: str


class AgentQuiz(BaseModel):
    topic: str = Field(
        min_length=2,
        max_length=100
    )

    no_of_questions: int = Field(
        ge=1,
        le=15,
        default=5
    )

    questions: List[AgentQuestion]


class QuestionResponse(BaseModel):
    id: int

    question_text: str

    option_a: str
    option_b: str
    option_c: str
    option_d: str


class QuizResponse(BaseModel):
    quiz_id: int

    topic: str = Field(
        min_length=2,
        max_length=100
    )

    no_of_questions: int = Field(
        ge=1,
        default=5
    )

    questions: List[QuestionResponse]


class AnswerResponse(BaseModel):
    question: str

    correct_answer: Literal["A", "B", "C", "D"]

    explanation: str


class QuizAnswersResponse(BaseModel):
    quiz_id: int

    topic: str = Field(
        min_length=2,
        max_length=100
    )

    answers: List[AnswerResponse]



class QuizListItem(BaseModel):
    quiz_id: int
    topic: str
    no_of_questions: int
    created_at: datetime
    attempted: bool = False
