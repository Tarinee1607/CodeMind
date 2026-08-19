from sqlalchemy.orm import Session
from app.models.revoked_token import RevokedToken
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token


def get_user_by_username(
    db: Session,
    username: str,
) -> User | None:

    return (
        db.query(User)
        .filter(User.username == username)
        .first()
    )


def get_user_by_email(
    db: Session,
    email: str,
) -> User | None:

    return (
        db.query(User)
        .filter(User.email == email)
        .first()
    )


def create_user(
    db: Session,
    username: str,
    email: str,
    password: str,
) -> User:

    hashed_password = hash_password(password)

    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

def authenticate_user(
    db: Session,
    username: str,
    password: str,
) -> User | None:

    user = get_user_by_username(db, username)

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user

def revoke_token(
    db: Session,
    token: str,
) -> None:
    existing_token = (
        db.query(RevokedToken)
        .filter(RevokedToken.token == token)
        .first()
    )

    if existing_token:
        return

    revoked_token = RevokedToken(token=token)

    db.add(revoked_token)
    db.commit()

def is_token_revoked(
    db: Session,
    token: str,
) -> bool:
    revoked_token = (
        db.query(RevokedToken)
        .filter(RevokedToken.token == token)
        .first()
    )

    return revoked_token is not None

