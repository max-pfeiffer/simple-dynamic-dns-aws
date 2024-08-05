"""Basic test fixtures."""

import pytest
from python_on_whales import DockerClient, Image, Builder, Container

from container.utils import get_docker_context, get_dockerfile
from tests.constants import TEST_IMAGE_TAG, PLATFORM, CONTAINER_PORT


@pytest.fixture(scope="session")
def docker_client() -> DockerClient:
    """Provide the Python on Whales docker client.

    :return:
    """
    return DockerClient(debug=True)


@pytest.fixture(scope="session")
def builder(docker_client: DockerClient) -> Builder:
    """Provide a Python on Whales BuildX builder instance.

    :param docker_client:
    :return:
    """
    builder: Builder = docker_client.buildx.create(
        driver="docker-container", driver_options=dict(network="host")
    )
    yield builder

    docker_client.buildx.stop(builder)
    docker_client.buildx.remove(builder)


@pytest.fixture(scope="session")
def docker_image(docker_client: DockerClient, builder: Builder) -> Image:
    image = docker_client.build(
        context_path=get_docker_context(),
        file=get_dockerfile(),
        tags=TEST_IMAGE_TAG,
        platforms=[PLATFORM],
        builder=builder,
        load=True,
    )
    yield image

    image.remove(force=True)


@pytest.fixture(scope="function")
def container(docker_client: DockerClient, docker_image: Image):
    dyn_dns_container: Container = docker_client.container.run(
        docker_image,
        platform=PLATFORM,
        publish=[(CONTAINER_PORT, CONTAINER_PORT)],
        detach=True,
    )

    yield dyn_dns_container

    dyn_dns_container.stop()
    dyn_dns_container.remove()


@pytest.fixture(scope="function")
def event() -> dict:
    return {
        "version": "2.0",
        "routeKey": "$default",
        "rawPath": "/path/to/resource",
        "rawQueryString": "parameter1=value1&parameter1=value2&parameter2=value",
        "cookies": ["cookie1", "cookie2"],
        "headers": {"Header1": "value1", "Header2": "value1,value2"},
        "queryStringParameters": {},
        "requestContext": {
            "accountId": "123456789012",
            "apiId": "api-id",
            "authentication": {
                "clientCert": {
                    "clientCertPem": "CERT_CONTENT",
                    "subjectDN": "www.example.com",
                    "issuerDN": "Example issuer",
                    "serialNumber": "a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1:a1",
                    "validity": {
                        "notBefore": "May 28 12:30:02 2019 GMT",
                        "notAfter": "Aug  5 09:36:04 2021 GMT",
                    },
                }
            },
            "authorizer": {
                "jwt": {
                    "claims": {"claim1": "value1", "claim2": "value2"},
                    "scopes": ["scope1", "scope2"],
                }
            },
            "domainName": "id.execute-api.us-east-1.amazonaws.com",
            "domainPrefix": "id",
            "http": {
                "method": "POST",
                "path": "/path/to/resource",
                "protocol": "HTTP/1.1",
                "sourceIp": "192.168.0.1/32",
                "userAgent": "agent",
            },
            "requestId": "id",
            "routeKey": "$default",
            "stage": "$default",
            "time": "12/Mar/2020:19:03:58 +0000",
            "timeEpoch": 1583348638390,
        },
        "body": "eyJ0ZXN0IjoiYm9keSJ9",
        "pathParameters": {"parameter1": "value1"},
        "isBase64Encoded": True,
        "stageVariables": {"stageVariable1": "value1", "stageVariable2": "value2"},
    }