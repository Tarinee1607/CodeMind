from pathlib import Path

from app.core.config import settings


def get_user_repository_root(user_id: int) -> Path:
    """
    Return the root directory where a user's repositories are stored.
    """
    root = Path(settings.REPOSITORY_FOLDER) / str(user_id)
    root.mkdir(parents=True, exist_ok=True)

    return root


def validate_repository_name(repository_name: str) -> str:
    """
    Validate and normalize a repository name before using it
    as a filesystem directory name.
    """
    name = repository_name.strip()

    if not name:
        raise ValueError("Repository name cannot be empty")

    if name in {".", ".."}:
        raise ValueError("Invalid repository name")

    if "/" in name or "\\" in name:
        raise ValueError("Repository name cannot contain path separators")

    if ":" in name:
        raise ValueError("Repository name cannot contain ':'")

    return name


def get_repository_path(
    user_id: int,
    repository_name: str,
) -> Path:
    """
    Return the local filesystem path for a specific repository.
    """
    name = validate_repository_name(repository_name)

    user_root = get_user_repository_root(user_id)

    repository_path = user_root / name

    return repository_path