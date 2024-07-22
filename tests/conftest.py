import pytest


@pytest.fixture(scope="session")
def test_environment(monkeypatch: pytest.MonkeyPatch):
    with monkeypatch.context() as mp:
        mp.setenv("AWS_SESSION_TOKEN", "test-token")
        yield
