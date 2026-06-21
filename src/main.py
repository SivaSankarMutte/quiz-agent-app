from fastapi import FastAPI

from app.db.database import engine
from app.db.models import Base

from app.router.quiz_router import router as quiz_router
from app.router.auth_router import router as auth_router
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"] # During development, many people temporarily use:
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(quiz_router)
app.include_router(auth_router)


