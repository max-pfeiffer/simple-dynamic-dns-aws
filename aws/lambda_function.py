"""AWS Lambda function."""

import json
import logging
import os
from typing import Optional

import boto3
from aws_secretsmanager_caching import SecretCache, SecretCacheConfig
from botocore.client import BaseClient
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel("INFO")

ROUTE_53_HOSTED_ZONE_ID: str = os.environ.get("ROUTE_53_HOSTED_ZONE_ID")
ROUTE_53_RECORD_TYPE: str = "A"
ROUTE_53_RECORD_TTL: int = 300


def route_53_client() -> BaseClient:
    """Instantiate the Route53 client.

    See: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/route53.html

    :return:
    """
    client = boto3.client("route53")
    return client


def secrets_manager_cache() -> SecretCache:
    """Instantiate the SecretsManager and it's cache.

    See: https://github.com/aws/aws-secretsmanager-caching-python?tab=readme-ov-file#usage

    :return:
    """
    client = boto3.client("secretsmanager")
    cache_config = SecretCacheConfig()
    cache = SecretCache(config=cache_config, client=client)
    return cache


def get_secret(secret_id: str) -> str:
    """Retrieve secret.

    See: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager/client/get_secret_value.html

    :param secret_id:
    :return:
    """
    logger.info(f"Retrieving secret for secret_id {secret_id}")
    cache = secrets_manager_cache()
    secret = cache.get_secret_string(secret_id)
    return secret


def get_dns_record(domain: str) -> Optional[str]:
    """Retrieve the DNS record for the given domain if it exists.

    See: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/route53/client/list_resource_record_sets.html

    :param domain:
    :return:
    """
    logger.info(f"Getting DNS record for {domain}")
    client = route_53_client()
    current_route53_record_set = client.list_resource_record_sets(
        HostedZoneId=ROUTE_53_HOSTED_ZONE_ID,
        StartRecordName=domain,
        StartRecordType=ROUTE_53_RECORD_TYPE,
    )
    try:
        resource_record_sets = current_route53_record_set["ResourceRecordSets"]
        matching_resource_record_set = next(
            resource_record_set
            for resource_record_set in resource_record_sets
            if resource_record_set["Name"] == f"{domain}."
        )
        current_route53_ip = matching_resource_record_set["ResourceRecords"][0]["Value"]
    except (KeyError, IndexError):
        logger.info(f"Could not find IP address for domain {domain}")
        current_route53_ip = None
    return current_route53_ip


def set_dns_record(domain: str, ip: str):
    """Change the DNS record for the given domain.

    See: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/route53/client/change_resource_record_sets.html

    :param domain:
    :param ip:
    :return:
    """
    logger.info(f"Setting DNS record for {domain} with IP address {ip}")
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
    """Lambda handler.

    :param event:
    :param context:
    :return:
    """
    logger.info(f"ROUTE_53_HOSTED_ZONE_ID: {ROUTE_53_HOSTED_ZONE_ID}")
    # Checking if all request parameters are present
    query_parameters = event["queryStringParameters"]
    try:
        client_id = query_parameters["client_id"]
        domain = query_parameters["domain"]
        ip = query_parameters["ip"]
        token = query_parameters["token"]
    except KeyError:
        logger.error("Missing query parameters")
        return {"statusCode": 400, "body": json.dumps("Missing request parameters")}

    # Check if token is valid
    expected_token = get_secret(client_id)
    if token != expected_token:
        logger.error("Invalid token")
        return {"statusCode": 401, "body": json.dumps("Invalid token")}

    try:
        current_ip = get_dns_record(domain)
        if current_ip is None:
            set_dns_record(domain, ip)
        else:
            if current_ip == ip:
                logger.info("DNS record matched and was not updated")
                return {
                    "statusCode": 200,
                    "body": json.dumps(
                        "Success: DNS record matched and was not updated"
                    ),
                }
            else:
                set_dns_record(domain, current_ip)

        logger.info("DNS record was updated")
        return {
            "statusCode": 200,
            "body": json.dumps("Success: DNS record was updated"),
        }
    except ClientError as exc:
        message = str(exc)
        logger.exception(message)
        return {"statusCode": 500, "body": json.dumps(message)}
    except Exception:
        logger.exception("Unexpected error")
        return {"statusCode": 500, "body": json.dumps("Something went wrong")}
