from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

from dotenv import load_dotenv
import os
from config.settings import settings

load_dotenv()

host = settings.POSTGRES_HOST
port = settings.POSTGRES_PORT
username = settings.POSTGRES_USER
password = settings.POSTGRES_PASSWORD
dbname = settings.POSTGRES_DB

DATABASE_URL = (
    f"postgresql://{username}:{password}@{host}:{port}/{dbname}"
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()