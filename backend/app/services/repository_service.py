from sqlalchemy.orm import Session

from app.models.repository import Repository


def create_repository(
    db: Session,
    user_id: int,
    name: str,
    source_type: str,
    source_url: str | None,
    local_path: str,
) -> Repository:
    repository = Repository(
        user_id=user_id,
        name=name,
        source_type=source_type,
        source_url=source_url,
        local_path=local_path,
        status="pending",
    )

    db.add(repository)
    db.commit()
    db.refresh(repository)

    return repository


def get_user_repositories(
    db: Session,
    user_id: int,
) -> list[Repository]:
    return (
        db.query(Repository)
        .filter(Repository.user_id == user_id)
        .order_by(Repository.created_at.desc())
        .all()
    )


def get_repository_by_id(
    db: Session,
    repository_id: int,
    user_id: int,
) -> Repository | None:
    return (
        db.query(Repository)
        .filter(
            Repository.id == repository_id,
            Repository.user_id == user_id,
        )
        .first()
    )

def update_repository(
    db: Session,
    repository: Repository,
    name: str | None = None,
    source_type: str | None = None,
    source_url: str | None = None,
) -> Repository:
    if name is not None:
        repository.name = name

    if source_type is not None:
        repository.source_type = source_type

    if source_url is not None:
        repository.source_url = source_url

    db.commit()
    db.refresh(repository)

    return repository

def delete_repository(
    db: Session,
    repository: Repository,
) -> None:
    db.delete(repository)
    db.commit()