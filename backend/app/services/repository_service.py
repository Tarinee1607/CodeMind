from pathlib import Path
import os
import stat
import shutil
from sqlalchemy.orm import Session

from app.models.repository import Repository
from app.services.git_service import clone_repository
from app.services.repository_manager import (
    get_repository_path,
)


def create_repository(
    db: Session,
    user_id: int,
    name: str,
    source_type: str,
    source_url: str | None,
    local_path: str,
) -> Repository:

    if source_type.lower() != "github":
        raise ValueError("Unsupported repository source type")

    if not source_url:
        raise ValueError("Source URL is required for GitHub repositories")

    repository_path = get_repository_path(
        user_id,
        name,
    )

    if repository_path.exists():
        raise FileExistsError(
            "Repository destination already exists"
        )

    repository = Repository(
        user_id=user_id,
        name=name,
        source_type=source_type,
        source_url=source_url,
        local_path=str(repository_path),
        status="pending",
    )

    db.add(repository)
    db.commit()
    db.refresh(repository)

    try:
        repository.status = "cloning"
        db.commit()

        clone_repository(
            source_url,
            repository_path,
        )

        repository.status = "ready"
        db.commit()
        db.refresh(repository)

        return repository

    except Exception:
        repository.status = "failed"
        db.commit()

        if repository_path.exists():
            import shutil

            shutil.rmtree(repository_path)

        db.delete(repository)
        db.commit()

        raise


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
    repository_path = Path(repository.local_path)

    def remove_readonly(func, path, exc_info):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    try:
        if repository_path.exists():
            shutil.rmtree(
                repository_path,
                onerror=remove_readonly,
            )

        db.delete(repository)
        db.commit()

    except Exception:
        db.rollback()
        raise