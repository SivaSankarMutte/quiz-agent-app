from pydantic import BaseModel


class LeaderboardEntry(BaseModel):
    username: str
    score: int
    total_questions: int