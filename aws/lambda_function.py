"""AWS Lambda function."""

import json
import logging
import os
from collections import namedtuple

import boto3
from aws_secretsmanager_caching import SecretCache, SecretCacheConfig
from botocore.client import BaseClient
from botocore.exceptions import ClientError

DnsRecord = namedtuple("DnsRecord", ["domain", "ip"])

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


def get_dns_records(domains: list[str]) -> list[DnsRecord]:
    """Retrieve the DNS records for the given domains if they exist.

    See: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/route53/client/list_resource_record_sets.html

    :param domain:
    :return:
    """
    logger.info(f"Getting DNS record for {domains}")
    client = route_53_client()
    current_route53_record_set = client.list_resource_record_sets(
        HostedZoneId=ROUTE_53_HOSTED_ZONE_ID,
        StartRecordType=ROUTE_53_RECORD_TYPE,
    )
    dns_records = []
    for domain in domains:
        try:
            resource_record_sets = current_route53_record_set["ResourceRecordSets"]
            matching_resource_record_set = next(
                resource_record_set
                for resource_record_set in resource_record_sets
                if resource_record_set["Name"] == f"{domain}."
            )
            current_route53_ip = matching_resource_record_set["ResourceRecords"][0][
                "Value"
            ]
            dns_records.append(DnsRecord(domain=domain, ip=current_route53_ip))
        except (KeyError, IndexError, StopIteration):
            logger.info(f"Could not find IP address for domain {domain}")
            dns_records.append(DnsRecord(domain=domain, ip=None))
    return dns_records


def set_dns_records(dns_records: list[DnsRecord], ip: str):
    """Change the DNS record for the given domain.

    See: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/route53/client/change_resource_record_sets.html

    :param dns_records:
    :param ip:
    :return:
    """
    changes: list[dict] = []
    for dns_record in dns_records:
        if (dns_record.ip is None) or (dns_record.ip != ip):
            logger.info(
                f"DNS record for domain {dns_record.domain} "
                f"will be updated with ip {ip}"
            )
            change = {
                "Action": "UPSERT",
                "ResourceRecordSet": {
                    "Name": dns_record.domain,
                    "Type": ROUTE_53_RECORD_TYPE,
                    "TTL": ROUTE_53_RECORD_TTL,
                    "ResourceRecords": [{"Value": ip}],
                },
            }
            changes.append(change)
        else:
            logger.info(
                f"DNS record for domain {dns_record.domain} "
                f"matched and will not be updated"
            )

    if changes:
        client = route_53_client()
        client.change_resource_record_sets(
            HostedZoneId=ROUTE_53_HOSTED_ZONE_ID,
            ChangeBatch={"Changes": changes},
        )


def lambda_handler(event: dict, context: dict):
    """Lambda handler.

    :param event:
    :param context:
    :return:
    """
    logger.info(f"ROUTE_53_HOSTED_ZONE_ID: {ROUTE_53_HOSTED_ZONE_ID}")
    # Checking if all request parameters are present
    query_parameters: dict = event["queryStringParameters"]
    try:
        client_id: str = query_parameters["client_id"]
        domains: list[str] = query_parameters["domain"].split(",")
        ip: str = query_parameters["ip"]
        token: str = query_parameters["token"]
    except KeyError:
        logger.error("Missing query parameters")
        return {"statusCode": 400, "body": json.dumps("Missing request parameters")}

    # Check if token is valid
    expected_token = get_secret(client_id)
    if token != expected_token:
        logger.error("Invalid token")
        return {"statusCode": 401, "body": json.dumps("Invalid token")}

    try:
        dns_records = get_dns_records(domains)
        set_dns_records(dns_records, ip)
        logger.info("DNS record was updated")
        return {
            "statusCode": 200,
            "body": json.dumps("DNS record was updated"),
        }
    except ClientError as exc:
        message = str(exc)
        logger.exception(message)
        return {"statusCode": 500, "body": json.dumps(message)}
    except Exception:
        logger.exception("Unexpected error")
        return {"statusCode": 500, "body": json.dumps("Something went wrong")}
