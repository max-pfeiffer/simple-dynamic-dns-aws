import json
import os
from typing import Optional

import boto3
import requests
from botocore.exceptions import ClientError
from botocore.client import BaseClient

SECRETS_EXTENSION_HTTP_PORT: str = "2773"
ROUTE_53_HOSTED_ZONE_ID: str = os.environ.get("ROUTE_53_HOSTED_ZONE_ID")
ROUTE_53_RECORD_TYPE: str = "A"
ROUTE_53_RECORD_TTL: int = 300


def route_53_client() -> BaseClient:
    client = boto3.client("route53")
    return client


def get_secret(secret_id: str) -> str:
    """Retrieve cached secret via Lambda extension.

    See: https://docs.aws.amazon.com/secretsmanager/latest/userguide/retrieving-secrets_lambda.html

    :param secret_id:
    :return:
    """
    headers = {"X-Aws-Parameters-Secrets-Token": os.environ.get("AWS_SESSION_TOKEN")}
    secrets_extension_endpoint = f"http://localhost:{SECRETS_EXTENSION_HTTP_PORT}/secretsmanager/get?secretId={secret_id}"

    response = requests.get(secrets_extension_endpoint, headers=headers)
    response.raise_for_status()

    secret = response.json()["SecretString"]
    return secret


def get_dns_record(domain: str) -> Optional[str]:
    """Retrieve the DNS record for the given domain if it exists.

    See: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/route53/client/list_resource_record_sets.html

    :param domain:
    :return:
    """
    client = route_53_client()
    current_route53_record_set = client.list_resource_record_sets(
        HostedZoneId=ROUTE_53_HOSTED_ZONE_ID,
        StartRecordName=domain,
        StartRecordType=ROUTE_53_RECORD_TYPE,
    )
    try:
        current_route53_ip = current_route53_record_set["ResourceRecordSets"][0][
            "ResourceRecords"
        ][0]["Value"]
    except KeyError:
        current_route53_ip = None
    return current_route53_ip


def set_dns_record(domain: str, ip: str):
    """Change the DNS record for the given domain.

    See: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/route53/client/change_resource_record_sets.html

    :param domain:
    :param ip:
    :return:
    """
    client = route_53_client()
    client.change_resource_record_sets(
        HostedZoneId=ROUTE_53_HOSTED_ZONE_ID,
        ChangeBatch={
            "Changes": [
                {
                    "Action": "UPSERT",
                    "ResourceRecordSet": {
                        "Name": domain,
                        "Type": ROUTE_53_RECORD_TYPE,
                        "TTL": ROUTE_53_RECORD_TTL,
                        "ResourceRecords": [{"Value": ip}],
                    },
                }
            ]
        },
    )


def lambda_handler(event: dict, context: dict):
    query_parameters = event["queryStringParameters"]
    # Checking if all request parameters are present
    try:
        client_id = query_parameters["client_id"]
        domain = query_parameters["domain"]
        ip = query_parameters["ip"]
        token = query_parameters["token"]
    except KeyError:
        return {"statusCode": 400, "body": json.dumps("Missing request parameters")}

    # Check if token is valid
    expected_token = get_secret(client_id)
    if token != expected_token:
        return {"statusCode": 401, "body": json.dumps("Invalid token")}

    try:
        current_ip = get_dns_record(domain)
        if current_ip is None:
            set_dns_record(domain, ip)
        else:
            if current_ip == ip:
                return {
                    "statusCode": 200,
                    "body": json.dumps(
                        "Success: DNS record matched and was not updated"
                    ),
                }
            else:
                set_dns_record(domain, current_ip)
        return {
            "statusCode": 200,
            "body": json.dumps("Success: DNS record was updated"),
        }
    except ClientError as exc:
        message = str(exc)
        return {"statusCode": 500, "body": json.dumps(message)}
    except Exception:
        return {"statusCode": 500, "body": json.dumps("Something went wrong")}
