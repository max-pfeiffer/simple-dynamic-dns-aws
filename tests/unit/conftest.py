import pytest
from pytest_mock import MockerFixture


@pytest.fixture(scope="function")
def mocked_route_53_client(monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture):
    with monkeypatch.context() as mp:
        mocked_route_53_client = mocker.MagicMock()

        def get_mocked_route_53_client():
            return mocked_route_53_client

        mp.setattr("aws.lambda_function.route_53_client", get_mocked_route_53_client)
        yield mocked_route_53_client


@pytest.fixture(scope="function")
def mocked_secrets_manager(monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture):
    with monkeypatch.context() as mp:
        mocked_secrets_manager = mocker.MagicMock()

        def get_mocked_secrets_manager():
            return mocked_secrets_manager

        mp.setattr("aws.lambda_function.secrets_manager", get_mocked_secrets_manager)
        yield mocked_secrets_manager
