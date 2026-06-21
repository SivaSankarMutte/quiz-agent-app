from crewai import Agent, Crew, Task, Process, LLM

from crewai.project import CrewBase, agent, task, crew

from app.schemas.quiz import AgentQuiz
from config.settings import settings


@CrewBase
class QuizCrew:

    agents_config = "agents.yaml"
    tasks_config = "tasks.yaml"

    llm = LLM(
        model="groq/llama-3.3-70b-versatile",
        api_key=settings.GROQ_API_KEY # for docker push it is needed/good to explicitly pass the api_key
    )

    @agent
    def quiz_creator(self) -> Agent:
        return Agent(
            config=self.agents_config["quiz_creator"],
            llm=self.llm,
            verbose=True
        )

    @agent
    def quiz_validator(self) -> Agent:
        return Agent(
            config=self.agents_config["quiz_validator"],
            llm=self.llm,
            verbose=True
        )

    @task
    def create_quiz(self) -> Task:
        return Task(
            config=self.tasks_config["create_quiz"]
        )

    @task
    def validate_quiz(self) -> Task:
        return Task(
            config=self.tasks_config["validate_quiz"],
            output_pydantic=AgentQuiz
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )