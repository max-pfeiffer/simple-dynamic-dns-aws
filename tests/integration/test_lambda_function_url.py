"""Tests for deployed Lambda function."""

import os

import requests


# @pytest.mark.skip
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
