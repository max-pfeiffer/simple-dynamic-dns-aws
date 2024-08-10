"""Test utilities."""

import os
from pathlib import Path


def get_docker_context() -> Path:
    """Docker build context path.

    :return:
    """
    return Path(__file__).parent.parent.resolve()


def get_dockerfile() -> Path:
    """Dockerfile path.

    :return:
    """
    docker_file_path = (
        Path(__file__).parent.parent.resolve() / "container" / "Dockerfile"
    )
    return docker_file_path


def running_on_github_actions() -> bool:
    """Check if running on GitHub Actions.

    :return:
    """
    bool_value = os.environ.get("GITHUB_ACTIONS", "false") == "true"
    return bool_value
