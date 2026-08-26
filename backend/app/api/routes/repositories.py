from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.schemas.repository import (
    RepositoryCreate,
    RepositoryResponse,
    RepositoryUpdate,
)
from app.services.repository_service import (
    create_repository,
    delete_repository,
    get_repository_by_id,
    get_user_repositories,
    update_repository,
)


router = APIRouter(
    prefix="/repositories",
    tags=["Repositories"],
)


@router.get(
    "",
    response_model=list[RepositoryResponse],
)
def list_repositories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_repositories(
        db=db,
        user_id=current_user.id,
    )


@router.post(
    "",
    response_model=RepositoryResponse,
    status_code=201,
)
def create_new_repository(
    repository_data: RepositoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_repository(
        db=db,
        user_id=current_user.id,
        name=repository_data.name,
        source_type=repository_data.source_type,
        source_url=repository_data.source_url,
        local_path="",
    )


@router.get(
    "/{repository_id}",
    response_model=RepositoryResponse,
)
def get_repository(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repository = get_repository_by_id(
        db=db,
        repository_id=repository_id,
        user_id=current_user.id,
    )

    if not repository:
        raise HTTPException(
            status_code=404,
            detail="Repository not found",
        )

    return repository


@router.put(
    "/{repository_id}",
    response_model=RepositoryResponse,
)
def update_existing_repository(
    repository_id: int,
    repository_data: RepositoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repository = get_repository_by_id(
        db=db,
        repository_id=repository_id,
        user_id=current_user.id,
    )

    if not repository:
        raise HTTPException(
            status_code=404,
            detail="Repository not found",
        )

    return update_repository(
        db=db,
        repository=repository,
        name=repository_data.name,
        source_type=repository_data.source_type,
        source_url=repository_data.source_url,
    )


@router.delete(
    "/{repository_id}",
    status_code=204,
)
def remove_repository(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repository = get_repository_by_id(
        db=db,
        repository_id=repository_id,
        user_id=current_user.id,
    )

    if not repository:
        raise HTTPException(
            status_code=404,
            detail="Repository not found",
        )

    delete_repository(
        db=db,
        repository=repository,
    )