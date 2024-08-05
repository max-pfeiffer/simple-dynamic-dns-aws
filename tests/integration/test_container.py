"""Tests for Docker container."""

import os
from time import sleep

import pytest
import requests

from tests.constants import EXPOSED_CONTAINER_PORT


@pytest.mark.usefixtures("container")
def test_container_missing_request_parameters(event: dict):
    """Test the container with missing parameters.

    :param event:
    :return:
    """
    sleep(3)
    url = f"http://localhost:{EXPOSED_CONTAINER_PORT}/2015-03-31/functions/function/invocations"

    response = requests.post(url, json=event)
    assert response.status_code == 200

    response_content: dict = response.json()

    assert response_content["statusCode"] == 400
    assert "Missing request parameters" in response_content["body"]


@pytest.mark.usefixtures("container")
def test_container_with_request_parameters(event: dict):
    """Test the container with proper request parameters.

    :param event:
    :return:
    """
    sleep(3)
    url = f"http://localhost:{EXPOSED_CONTAINER_PORT}/2015-03-31/functions/function/invocations"
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

    response_content: dict = response.json()

    assert "You must specify a region." in response_content["errorMessage"]
