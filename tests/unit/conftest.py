import pytest
from pytest_mock import MockerFixture


@pytest.fixture(scope="function")
def mocked_route_53_client(monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture):
    with monkeypatch.context() as mp:
        mocked_route_53_client = mocker.MagicMock()

        def get_mocked_route_53_client():
            return mocked_route_53_client

        mp.setenv("AWS_SESSION_TOKEN", "test-token")
        mp.setattr("aws.lambda_function.route_53_client", get_mocked_route_53_client)
        yield mocked_route_53_client
