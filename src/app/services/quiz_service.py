from fastapi import HTTPException
import json

from sqlalchemy.orm import Session

from app.db.models import Quiz, Question, QuizAttempt, User
from app.cache.redis_client import redis_client
from agents.crew import QuizCrew
from app.schemas.quiz import AgentQuiz, QuizListItem
from app.schemas.leaderboard import LeaderboardEntry
from app.schemas.attempt import AttemptResponse


class QuizService:

    CACHE_EXPIRY = 86400

    @staticmethod
    def build_cache_key(topic: str) -> str:
        return (
            f"quiz:{topic.lower().strip().replace(' ', '_')}"
        )

    def get_quiz_from_cache(
        self,
        topic: str
    ):

        key = self.build_cache_key(topic)

        data = redis_client.get(key)

        if not data:
            return None

        return json.loads(data)

    def save_quiz_to_cache(
        self,
        topic: str,
        quiz_data: dict
    ):

        key = self.build_cache_key(topic)

        redis_client.set(
            key,
            json.dumps(quiz_data),
            ex=self.CACHE_EXPIRY
        )

    def get_quiz_by_topic(
        self,
        db: Session,
        topic: str
    ):

        return (
            db.query(Quiz)
            .filter(Quiz.topic == topic)
            .first()
        )

    def generate_quiz(
        self,
        topic: str,
        no_of_questions: int = 5
    ) -> AgentQuiz:

        result = (
            QuizCrew()
            .crew()
            .kickoff(
                inputs={
                    "topic": topic,
                    "no_of_questions": no_of_questions
                }
            )
        )

        return result.pydantic

    def save_quiz(
        self,
        db: Session,
        agent_quiz: AgentQuiz
    ) -> Quiz:

        quiz = Quiz(
            topic=agent_quiz.topic,
            no_of_questions=agent_quiz.no_of_questions,
            is_validated=True
        )

        db.add(quiz)

        db.flush()

        for q in agent_quiz.questions:

            question = Question(
                quiz_id=quiz.id,
                question_text=q.question_text,
                option_a=q.option_a,
                option_b=q.option_b,
                option_c=q.option_c,
                option_d=q.option_d,
                correct_answer=q.correct_answer,
                explanation=q.explanation
            )

            db.add(question)

        db.commit()

        db.refresh(quiz)

        return quiz

    def quiz_to_dict(
        self,
        quiz: Quiz
    ):

        return {
            "quiz_id": quiz.id,
            "topic": quiz.topic,
            "questions": [
                {
                    "id": q.id,
                    "question_text": q.question_text,
                    "option_a": q.option_a,
                    "option_b": q.option_b,
                    "option_c": q.option_c,
                    "option_d": q.option_d
                }
                for q in quiz.questions
            ]
        }

    def get_or_create_quiz(
        self,
        db: Session,
        topic: str,
        no_of_questions: int
    ):

        cached_quiz = self.get_quiz_from_cache(topic)

        if cached_quiz:
            print("Returning from Redis")
            return cached_quiz

        existing_quiz = self.get_quiz_by_topic(
            db,
            topic
        )

        if existing_quiz:

            print("Returning from PostgreSQL")

            response = self.quiz_to_dict(
                existing_quiz
            )

            self.save_quiz_to_cache(
                topic,
                response
            )

            return response

        print("Generating using CrewAI")

        agent_quiz = self.generate_quiz(
            topic,
            no_of_questions=no_of_questions
        )

        quiz = self.save_quiz(
            db,
            agent_quiz
        )

        db.refresh(quiz)

        response = self.quiz_to_dict(
            quiz
        )

        self.save_quiz_to_cache(
            topic,
            response
        )

        return response

    def get_answers(
        self,
        db: Session,
        quiz_id: int
    ):

        quiz = (
            db.query(Quiz)
            .filter(
                Quiz.id == quiz_id
            )
            .first()
        )

        if not quiz:
            return None

        return {
            "quiz_id": quiz.id,
            "topic": quiz.topic,
            "answers": [
                {
                    "question": q.question_text,
                    "correct_answer": q.correct_answer,
                    "explanation": q.explanation
                }
                for q in quiz.questions
            ]
        }
    

    def submit_quiz(
        self,
        db: Session,
        quiz_id: int,
        user_id: int,
        answers: list
    ):
        
        existing_attempt = (
            db.query(QuizAttempt)
            .filter(
                QuizAttempt.user_id == user_id,
                QuizAttempt.quiz_id == quiz_id
            )
            .first()
        )

        if existing_attempt:
            raise HTTPException(
                status_code=400,
                detail="Quiz already attempted"
            )
        
        quiz = (
            db.query(Quiz)
            .filter(Quiz.id == quiz_id)
            .first()
        )

        if not quiz:
            return None

        question_map = {
            question.id: question
            for question in quiz.questions
        }

        score = 0

        for answer in answers:

            question = question_map.get(
                answer.question_id
            )

            if not question:
                continue

            if (
                answer.selected_answer.upper()
                ==
                question.correct_answer.upper()
            ):
                score += 1

        attempt = QuizAttempt(
            user_id=user_id,
            quiz_id=quiz_id,
            score=score,
            total_questions=len(
                quiz.questions
            )
        )

        db.add(attempt)
        db.commit()

        percentage = round(
            (score / len(quiz.questions)) * 100,
            2
        )

        return {
            "score": score,
            "total_questions": len(
                quiz.questions
            ),
            "percentage": percentage
        }
    
    def get_leaderboard(
        self,
        db: Session,
        quiz_id: int
    ):
        
        results = (
            db.query(
                User.username,
                QuizAttempt.score,
                QuizAttempt.total_questions
            )
            .join(
                QuizAttempt,
                User.id == QuizAttempt.user_id
            )
            .filter(
                QuizAttempt.quiz_id == quiz_id
            )
            .order_by(
                QuizAttempt.score.desc()
            )
            .all()
        )


        return [
            LeaderboardEntry(
                username=row.username,
                score=row.score,
                total_questions=row.total_questions
            )
            for row in results
        ]
    
    def get_user_attempts(
        self,
        db: Session,
        user_id: int
    ):
        
        attempts = (
            db.query(
                QuizAttempt,
                Quiz.topic
            )
            .join(
                Quiz,
                Quiz.id == QuizAttempt.quiz_id
            )
            .filter(
                QuizAttempt.user_id == user_id
            )
            .order_by(
                QuizAttempt.attempted_at.desc()
            )
            .all()
        )

        return [
            AttemptResponse(
                quiz_id=attempt.quiz_id,
                topic=topic,
                score=attempt.score,
                total_questions=attempt.total_questions,
                attempted_at=attempt.attempted_at
            )
            for attempt, topic in attempts
        ]

    def get_quiz(
        self,
        db: Session,
        quiz_id: int
    ):

        quiz = (
            db.query(Quiz)
            .filter(Quiz.id == quiz_id)
            .first()
        )

        if not quiz:
            return None

        return {
            "quiz_id": quiz.id,
            "topic": quiz.topic,
            "no_of_questions": quiz.no_of_questions,
            "questions": [
                {
                    "id": q.id,
                    "question_text": q.question_text,
                    "option_a": q.option_a,
                    "option_b": q.option_b,
                    "option_c": q.option_c,
                    "option_d": q.option_d,
                }
                for q in quiz.questions
            ]
        }
    


    def get_all_quizzes(
        self,
        db: Session,
        current_user_id: int
    ):
        quizzes = (
            db.query(Quiz)
            .order_by(
                Quiz.created_at.desc()
            )
            .all()
        )

        return [
            QuizListItem(
                quiz_id=quiz.id,
                topic=quiz.topic,
                created_at=quiz.created_at.isoformat(),
                no_of_questions=quiz.no_of_questions,
                attempted=(
                    db.query(QuizAttempt)
                    .filter(
                        QuizAttempt.quiz_id == quiz.id,
                        QuizAttempt.user_id == current_user_id
                    )
                    .first() is not None
                )
            )
            for quiz in quizzes
        ]