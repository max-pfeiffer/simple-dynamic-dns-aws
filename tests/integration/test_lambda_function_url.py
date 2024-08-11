"""Tests for deployed Lambda function."""

import os

import pytest
import requests

from tests.utils import running_on_github_actions


@pytest.mark.skipif(
    running_on_github_actions(),
    reason="Environment variables are not configured on GitHub Actions",
)
def test_lambda_function_url():
    """Test the deployed AWS Lambda function.

    :return:
    """
    url = os.environ.get("LAMBDA_FUNCTION_URL")
    client_id = os.environ.get("CLIENT_ID")
    domain = os.environ.get("DOMAIN")
    ip = os.environ.get("IP")
    token = os.environ.get("TOKEN")

    params = {
        "client_id": client_id,
        "domain": domain,
        "ip": ip,
        "token": token,
    }

    response = requests.get(url, params=params)
    assert response.status_code == 200
