"""Tests for Docker container."""

import os

import requests
from python_on_whales import DockerClient, Image

from tests.constants import EXPOSED_CONTAINER_PORT, PLATFORM


def test_container(docker_client: DockerClient, docker_image: Image, event: dict):
    """Test the container.

    :param event:
    :return:
    """
    with docker_client.container.run(
        docker_image,
        platform=PLATFORM,
        publish=[(EXPOSED_CONTAINER_PORT, "8080")],
        detach=True,
        interactive=True,
        tty=True,
    ):
        # Test the container with missing parameters
        url = f"http://localhost:{EXPOSED_CONTAINER_PORT}/2015-03-31/functions/function/invocations"

        response = requests.post(url, json=event)
        assert response.status_code == 200

        response_content: dict = response.json()

        assert response_content["statusCode"] == 400
        assert "Missing request parameters" in response_content["body"]

        # Test the container with proper request parameters
        client_id = os.environ.get("CLIENT_ID")
        domain = os.environ.get("DOMAIN")
        ip = os.environ.get("IP")
        token = os.environ.get("TOKEN")

        event["queryStringParameters"] = {
            "client_id": client_id,
            "domain": domain,
            "ip": ip,
            "token": token,
        }

        response = requests.post(url, json=event)
        assert response.status_code == 200
