[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![codecov](https://codecov.io/gh/max-pfeiffer/simple-dynamic-dns-aws/graph/badge.svg?token=8btmoZksZb)](https://codecov.io/gh/max-pfeiffer/simple-dynamic-dns-aws)
![pipeline workflow](https://github.com/max-pfeiffer/simple-dynamic-dns-aws/actions/workflows/pipeline.yaml/badge.svg)

# Simple Dynamic DNS with AWS
Simple and cost-efficient Dynamic DNS build with AWS Lamda and Route 53.

This project provides an AWS Lambda function with which you can set **A-records** dynamically for **one** domain
you have configured in AWS Route 53. For authentication, a token is used which is stored using AWS Secrets Manager.

Usually consumer grade routers (Linksys, AVM, etc.) provide a dynamic DNS feature which just supports calling a URL with
HTTP GET method. All dynamic DNS settings need to be sent via URL query parameters.

This project uses an ARM64 Docker image as it is more cost-efficient to run AWS Lambda functions on ARM64 architecture.

If you want to cover this use case, this project is for you.

## Usage
### Manual configuration
1. Create a private container registry in AWS ECR
2. Build and push the Docker image to that registry:
   ```shell
    aws ecr get-login-password --region <your region> | docker login --username AWS --password-stdin <your ECR registry>
    docker build -t simple-dyn-dns --platform linux/arm64 -f ./container/Dockerfile .
    docker tag simple-dyn-dns:latest <your ECR registry>simple-dyn-dns:latest
    docker push <your ECR registry>/simple-dyn-dns:latest
   ```
3. Add secret in AWS Secrets Manager:
   1. configure a secure token for your client_id
4. [Create a AWS Lambda function](https://docs.aws.amazon.com/lambda/latest/dg/getting-started.html):
   1. use the just created Docker image from AWS ECR for the function
   2. [configure environment variables for the function](https://docs.aws.amazon.com/lambda/latest/dg/configuration-envvars.html):
      1. ROUTE_53_HOSTED_ZONE_ID (required)
      2. ROUTE_53_RECORD_TTL (optional, default=3600sec)
      3. SECRETS_MANAGER_REFRESH_INTERVAL (optional, default=86400sec)
   3. [configure an URL for AWS Lambda function](https://docs.aws.amazon.com/lambda/latest/dg/urls-configuration.html)
   4. [configure permissions for AWS Lambda function (execution role)](https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html):
      1. read secret from AWS Secrets Manager
      2. read and write DNS Records with AWS Route 53

You are ready to go! Configure your Router to call the AWS Lambda function URL with query parameters like this:
`https://uwigefgf8437rgeydbea2q40jedbl.lambda-url.eu-central-1.on.aws/?domain=www.example.com&ip=123.45.56.78&client_id=linksys_router&token=78234rtgf438g7g43r4bfi3784fgh`
