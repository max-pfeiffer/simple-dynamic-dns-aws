"""Tests for lambda_handler function."""

from secrets import token_hex
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from aws.lambda_function import lambda_handler


def test_lambda_handler(
    mocked_route_53_client: MagicMock, mocked_secrets_manager_cache: MagicMock
) -> None:
    """Test the happy path for lambda_handler().

    :param mocked_route_53_client:
    :param mocked_secrets_manager_cache:
    :return:
    """
    client_id = str(uuid4())
    test_token = token_hex()
    event: dict = {
        "queryStringParameters": {
            "client_id": client_id,
            "domain": "test_domain",
            "ip": "127.0.0.1",
            "token": test_token,
        }
    }
    mocked_secrets_manager_cache.get_secret_string.return_value = test_token

    response: dict = lambda_handler(event, {})

    assert response["statusCode"] == 200
    mocked_route_53_client.list_resource_record_sets.assert_called_once()
    mocked_route_53_client.change_resource_record_sets.assert_called_once()


def test_lambda_handler_invalid_token(
    mocked_route_53_client: MagicMock, mocked_secrets_manager_cache: MagicMock
) -> None:
    """Test calling lambda_handler() with an invalid token.

    :param mocked_route_53_client:
    :param mocked_secrets_manager_cache:
    :return:
    """
    client_id = str(uuid4())
    test_token = token_hex()
    event: dict = {
        "queryStringParameters": {
            "client_id": client_id,
            "domain": "test_domain",
            "ip": "127.0.0.1",
            "token": "invalid_token",
        }
    }
    mocked_secrets_manager_cache.get_secret_string.return_value = test_token

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
    event: dict,
    mocked_route_53_client: MagicMock,
    mocked_secrets_manager_cache: MagicMock,
) -> None:
    """Test lambda_handler() with a missing query parameters.

    :param event:
    :param mocked_route_53_client:
    :param mocked_secrets_manager_cache:
    :return:
    """
    response: dict = lambda_handler(event, {})

    assert response["statusCode"] == 400
    mocked_secrets_manager_cache.get_secret_string.assert_not_called()
    mocked_route_53_client.list_resource_record_sets.assert_not_called()
    mocked_route_53_client.change_resource_record_sets.assert_not_called()


@pytest.mark.parametrize(
    "domain, ip, result, dns_record_needs_update",
    [
        (
            "foo.bar",
            "123.134.84.62",
            "Success: DNS record matched and was not updated",
            False,
        ),
        (
            "boom.bang",
            "231.134.85.63",
            "Success: DNS record matched and was not updated",
            False,
        ),
        ("cling.clang", "156.167.66.66", "Success: DNS record was updated", True),
        ("foo.bar", "192.168.23.162", "Success: DNS record was updated", True),
        ("boom.bang", "231.134.85.64", "Success: DNS record was updated", True),
    ],
)
def test_lambda_handler_multiple_dns_entries(
    mocked_route_53_client: MagicMock,
    mocked_secrets_manager_cache: MagicMock,
    route_53_client_response: dict,
    domain: str,
    ip: str,
    result: str,
    dns_record_needs_update: bool,
) -> None:
    """Test if lambda_handler() deals correctly with multiple DNS records.

    :param mocked_route_53_client:
    :param mocked_secrets_manager_cache:
    :param route_53_client_response:
    :param domain:
    :param ip:
    :param result:
    :param dns_record_needs_update:
    :return:
    """
    client_id = str(uuid4())
    test_token = token_hex()
    event: dict = {
        "queryStringParameters": {
            "client_id": client_id,
            "domain": domain,
            "ip": ip,
            "token": test_token,
        }
    }
    mocked_secrets_manager_cache.get_secret_string.return_value = test_token
    mocked_route_53_client.list_resource_record_sets.return_value = (
        route_53_client_response
    )

    response: dict = lambda_handler(event, {})

    assert response["statusCode"] == 200
    assert result in response["body"]
    mocked_route_53_client.list_resource_record_sets.assert_called_once()
    if dns_record_needs_update:
        mocked_route_53_client.change_resource_record_sets.assert_called_once()
