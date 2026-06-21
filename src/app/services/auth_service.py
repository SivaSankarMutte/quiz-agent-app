from sqlalchemy.orm import Session

from app.db.models import User
from app.schemas.user import UserCreate
from app.auth.security import (
    hash_password,
    verify_password
)


def get_user_by_email(
    db: Session,
    email: str
) -> User | None:

    return (
        db.query(User)
        .filter(User.email == email)
        .first()
    )


def get_user_by_username(
    db: Session,
    username: str
) -> User | None:

    return (
        db.query(User)
        .filter(User.username == username)
        .first()
    )


def create_user(
    db: Session,
    user_data: UserCreate
) -> User:

    existing_email = get_user_by_email(
        db,
        user_data.email
    )

    if existing_email:
        raise ValueError(
            "Email already registered"
        )

    existing_username = get_user_by_username(
        db,
        user_data.username
    )

    if existing_username:
        raise ValueError(
            "Username already exists"
        )

    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(
            user_data.password
        )
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(
    db: Session,
    email: str,
    password: str
) -> User | None:

    user = get_user_by_email(
        db,
        email
    )

    if not user:
        return None

    if not verify_password(
        password,
        user.hashed_password
    ):
        return None

    return user


def get_user_by_id(
    db: Session,
    user_id: int
) -> User | None:

    return (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )