from unittest.mock import MagicMock

import pytest

from aws.lambda_function import lambda_handler, SECRETS_EXTENSION_HTTP_PORT
import responses
from secrets import token_hex
from uuid import uuid4


@responses.activate
def test_lambda_handler(mocked_route_53_client: MagicMock) -> None:
    client_id = str(uuid4())
    test_token = token_hex()
    secrets_extension_endpoint = f"http://localhost:{SECRETS_EXTENSION_HTTP_PORT}/secretsmanager/get?secretId={client_id}"
    responses.get(secrets_extension_endpoint, json={"SecretString": test_token})
    event: dict = {
        "queryStringParameters": {
            "client_id": client_id,
            "domain": "test_domain",
            "ip": "127.0.0.1",
            "token": test_token,
        }
    }
    response: dict = lambda_handler(event, {})

    assert response["statusCode"] == 200
    mocked_route_53_client.list_resource_record_sets.assert_called_once()
    mocked_route_53_client.change_resource_record_sets.assert_called_once()


@responses.activate
def test_lambda_handler_invalid_token(mocked_route_53_client: MagicMock) -> None:
    client_id = str(uuid4())
    test_token = token_hex()
    secrets_extension_endpoint = f"http://localhost:{SECRETS_EXTENSION_HTTP_PORT}/secretsmanager/get?secretId={client_id}"
    responses.get(secrets_extension_endpoint, json={"SecretString": test_token})
    event: dict = {
        "queryStringParameters": {
            "client_id": client_id,
            "domain": "test_domain",
            "ip": "127.0.0.1",
            "token": "invalid_token",
        }
    }
    response: dict = lambda_handler(event, {})

    assert response["statusCode"] == 401
    mocked_route_53_client.list_resource_record_sets.assert_not_called()
    mocked_route_53_client.change_resource_record_sets.assert_not_called()


@pytest.mark.parametrize(
    "event",
    [
        {
            "queryStringParameters": {
                "client_id": str(uuid4()),
                "domain": "test_domain",
                "ip": "127.0.0.1",
            }
        },
        {
            "queryStringParameters": {
                "client_id": str(uuid4()),
                "domain": "test_domain",
            }
        },
        {
            "queryStringParameters": {
                "client_id": str(uuid4()),
            }
        },
        {"queryStringParameters": {}},
    ],
)
def test_lambda_handler_missing_query_parameters(
    event: dict, mocked_route_53_client: MagicMock
) -> None:
    response: dict = lambda_handler(event, {})

    assert response["statusCode"] == 400
    mocked_route_53_client.list_resource_record_sets.assert_not_called()
    mocked_route_53_client.change_resource_record_sets.assert_not_called()
