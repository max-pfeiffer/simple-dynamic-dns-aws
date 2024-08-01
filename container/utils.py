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
    docker_file_path = Path(__file__).parent.resolve() / "Dockerfile"
    return docker_file_path
