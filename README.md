[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![codecov](https://codecov.io/gh/max-pfeiffer/simple-dynamic-dns-aws/graph/badge.svg?token=8btmoZksZb)](https://codecov.io/gh/max-pfeiffer/simple-dynamic-dns-aws)
![pipeline workflow](https://github.com/max-pfeiffer/simple-dynamic-dns-aws/actions/workflows/pipeline.yaml/badge.svg)

# Simple Dynamic DNS with AWS
Simple and cost-efficient Dynamic DNS build with AWS Lamda and Route 53.

This project provides an AWS Lambda function with which you can set **A-records** dynamically for **one** domain
you have configured in AWS Route 53. For authentication, a token is used which is stored using AWS Secrets Manager.

This project uses an ARM64 Docker image as it is more cost-efficient to run AWS Lambda functions on ARM64 architecture.

Usually consumer grade routers (Linksys, AVM, etc.) provide a dynamic DNS feature which just supports calling a URL with
HTTP GET method. All dynamic DNS settings need to be sent via URL query parameters.

Please also have a look at my [dynamic-dns-update-client](https://github.com/max-pfeiffer/dynamic-dns-update-client)
companion project. I created a CLI tool for sending IP address updates to dynamic DNS Servers or Dynamic DNS solution
like this here.

## Usage
### OpenTofu
I like infrastructure-as-code, so deployment is fully automated with [OpenTofu](https://opentofu.org/).

Prerequisites:
* [AWS CLI installed](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) and configured
* [OpenTofu installed](https://opentofu.org/docs/intro/install/)

In `opentofu` directory create your own `credentials.auto.tfvars` from `credentials.auto.tfvars.example` file
and edit it to your liking:
```shell
$ cp credentials.auto.tfvars.example credentials.auto.tfvars
$ vim credentials.auto.tfvars
```

Then do in `opentofu` directory what you usually need to do for [OpenTofu](https://opentofu.org/) provisioning:
```shell
$ tofu init
$ tofu plan
$ tofu apply
```
The infrastructure state isn't persisted in this repository as this is public. So you probably want to
fork/clone this repository and tweak the [.gitignore](.gitignore) file to your liking.

The Lambda function URL and API token are provided as output. As `api_token` is marked as security sensitive you need
to call for it specifically:
```shell
$ tofu output lambda_function_url
$ tofu output api_token
```

### Manual configuration
If you really want, you can also provision the AWS resources manually without [OpenTofu](https://opentofu.org/):
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

### Router configuration
#### Web UI
Many routers have a web user interface which lets you configure a Dyn DNS server by calling a URL. 
Configure your router to call the AWS Lambda function URL with query parameters like this:
`https://uwigefgf8437rgeydbea2q40jedbl.lambda-url.eu-central-1.on.aws/?domain=www.example.com&ip=123.45.56.78&client_id=myrouter&token=78234rtgf438g7g43r4bfi3784fgh`

#### OpenWRT
If you own a router with an [OpenWRT](https://openwrt.org/) operating system, you can also configure a
[dynamic DNS client through the LuCI web interface](https://openwrt.org/docs/guide-user/services/ddns/client)
or by other means.

I personally found that quite cumbersome and error-prone. Plus, I could not cover my use case with it properly, so I
wrote my own [dynamic-dns-update-client](https://github.com/max-pfeiffer/dynamic-dns-update-client).
It's easy to install on OpenWrt (if you happen to have some MB of free storage space).
[After installing it](https://github.com/max-pfeiffer/dynamic-dns-update-client?tab=readme-ov-file#openwrt),
you can you run it like this:
```shell
$ dynamic-dns-update-client https://uwigefgf8437rgeydbea2q40jedbl.lambda-url.eu-central-1.on.aws/ \
      --ip-address-provider openwrt_network \
      --ip-address-url-parameter-name ip \
      --url-parameter domain=www.example.com \
      --url-parameter client_id=myrouter \
      --url-parameter token=78234rtgf438g7g43r4bfi3784fgh
```
