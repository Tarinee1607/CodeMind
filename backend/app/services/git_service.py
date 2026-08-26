import subprocess
from pathlib import Path


def clone_repository(
    repository_url: str,
    destination: Path,
) -> None:
    """
    Clone a Git repository into the specified destination.
    """

    if not repository_url or not repository_url.strip():
        raise ValueError("Repository URL is required")

    repository_url = repository_url.strip()

    if destination.exists():
        raise FileExistsError(
            "Repository destination already exists"
        )

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    try:
        result = subprocess.run(
            [
                "git",
                "clone",
                repository_url,
                str(destination),
            ],
            capture_output=True,
            text=True,
            timeout=300,
        )

    except FileNotFoundError:
        raise RuntimeError(
            "Git is not installed or not available in PATH"
        )

    except subprocess.TimeoutExpired:
        raise RuntimeError(
            "Git clone operation timed out"
        )

    if result.returncode != 0:
        error_message = (
            result.stderr.strip()
            or result.stdout.strip()
            or "Git clone failed"
        )

        raise RuntimeError(error_message)