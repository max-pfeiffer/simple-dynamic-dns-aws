"""Tests for deployed Lambda function."""

import os

import pytest
import requests

from tests.utils import running_on_github_actions

DOMAIN_1 = os.environ.get("DOMAIN_1")
DOMAIN_2 = os.environ.get("DOMAIN_2")


@pytest.mark.skipif(
    running_on_github_actions(),
    reason="Environment variables are not configured on GitHub Actions",
)
@pytest.mark.parametrize(
    "domains",
    [
        [DOMAIN_1],
        [DOMAIN_1, DOMAIN_2],
    ],
)
def test_lambda_function_url(domains: list[str]):
    """Test the deployed AWS Lambda function.

    :return:
    """
    url = os.environ.get("LAMBDA_FUNCTION_URL")
    client_id = os.environ.get("CLIENT_ID")
    ip = os.environ.get("IP")
    token = os.environ.get("TOKEN")

    params = {
        "client_id": client_id,
        "domain": domains,
        "ip": ip,
        "token": token,
    }

    response = requests.get(url, params=params)
    assert response.status_code == 200
