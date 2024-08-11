"""Unit test fixtures."""

import pytest
from pytest_mock import MockerFixture


@pytest.fixture(scope="function")
def mocked_route_53_client(monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture):
    """Provide a mocked Route 53 client.

    :type monkeypatch: pytest.MonkeyPatch
    :param monkeypatch:
    :type mocker: MockerFixture
    :param mocker:
    :return:
    """
    with monkeypatch.context() as mp:
        mocked_route_53_client = mocker.MagicMock()

        def get_mocked_route_53_client():
            return mocked_route_53_client

        mp.setattr("aws.lambda_function.route_53_client", get_mocked_route_53_client)
        yield mocked_route_53_client


@pytest.fixture(scope="function")
def mocked_secrets_manager_cache(
    monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture
):
    """Provide a mocked secrets manager cache.

    :type monkeypatch: pytest.MonkeyPatch
    :param monkeypatch:
    :type mocker: MockerFixture
    :param mocker:
    :return:
    """
    with monkeypatch.context() as mp:
        mocked_secrets_manager_cache = mocker.MagicMock()

        def get_mocked_secrets_manager_cache():
            return mocked_secrets_manager_cache

        mp.setattr(
            "aws.lambda_function.secrets_manager_cache",
            get_mocked_secrets_manager_cache,
        )
        yield mocked_secrets_manager_cache


@pytest.fixture(scope="function")
def route_53_client_response() -> dict:
    """Provide a mocked route 53 client response.

    :return:
    """
    return {
        "ResponseMetadata": {
            "RequestId": "2c3fc3de-fcb7-4ae0-a6a3-5c11f454980f",
            "HTTPStatusCode": 200,
            "HTTPHeaders": {
                "x-amzn-requestid": "2c3fc3de-fcb7-4ae0-a6a3-5c11f454980f",
                "content-type": "text/xml",
                "content-length": "436",
                "date": "Mon, 05 Aug 2024 18:24:17 GMT",
            },
            "RetryAttempts": 0,
        },
        "ResourceRecordSets": [
            {
                "Name": "foo.bar.",
                "Type": "A",
                "TTL": 300,
                "ResourceRecords": [{"Value": "123.134.84.62"}],
            },
            {
                "Name": "boom.bang.",
                "Type": "A",
                "TTL": 300,
                "ResourceRecords": [{"Value": "231.134.85.63"}],
            },
        ],
        "IsTruncated": False,
        "MaxItems": "100",
    }
