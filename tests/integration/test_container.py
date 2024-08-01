import os

import requests
from python_on_whales import Container

from tests.constants import CONTAINER_PORT


def test_container_missing_request_parameters(container: Container, event: dict):
    url = f"http://localhost:{CONTAINER_PORT}/2015-03-31/functions/function/invocations"

    response = requests.post(url, json=event)
    assert response.status_code == 200

    response_content: dict = response.json()

    assert response_content["statusCode"] == 400
    assert "Missing request parameters" in response_content["body"]


def test_container_missing(container: Container, event: dict):
    url = "http://localhost:8080/2015-03-31/functions/function/invocations"
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

    assert (
        "/secretsmanager/get?secretId=avm-fritz-box" in response_content["errorMessage"]
    )
