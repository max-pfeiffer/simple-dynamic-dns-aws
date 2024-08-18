data "aws_region" "current" {}

data "aws_caller_identity" "this" {}

data "aws_ecr_authorization_token" "token" {}

data "toml_file" "example" {
  input = file(local.pyproject_toml)
}

terraform {
  required_providers {
   aws = {
      source = "hashicorp/aws"
      version = "5.63.0"
    }
    docker = {
      source = "kreuzwerker/docker"
      version = "3.0.2"
    }
    toml = {
      source  = "registry.terraform.io/tobotimus/toml"
      version = "0.3.0"
    }
  }
}

provider "aws" {
  # Make it faster by skipping checks and validations
  skip_metadata_api_check     = true
  skip_region_validation      = true
  skip_credentials_validation = true
}

provider "docker" {
  registry_auth {
    address  = format("%v.dkr.ecr.%v.amazonaws.com", data.aws_caller_identity.this.account_id, data.aws_region.current.name)
    username = data.aws_ecr_authorization_token.token.user_name
    password = data.aws_ecr_authorization_token.token.password
  }
}

resource "aws_secretsmanager_secret" "token" {
  name = local.secrets["CLIENT_ID"]
}

resource "aws_secretsmanager_secret_version" "token" {
  secret_id     = aws_secretsmanager_secret.token.id
  secret_string = local.secrets["TOKEN"]
}

module "docker_image" {
	source = "terraform-aws-modules/lambda/aws//modules/docker-build"

	create_ecr_repo = false
	ecr_repo = local.aws_name

	image_tag = data.toml_file.example.content.tool.poetry.version
    platform = "linux/arm64"
	source_path = "${local.repo_root}"
	docker_file_path = "container/Dockerfile"
}

module "lambda_function" {
  source = "terraform-aws-modules/lambda/aws"

  # Name and description
  function_name = local.aws_name
  description   = "Simple Dynamic DNS"

  # Function config
  create_package = false
  image_uri    = module.docker_image.image_uri
  package_type = "Image"
  architectures = ["arm64"]
  timeout = 5

  # Function URL
  create_lambda_function_url = true
  authorization_type = "NONE"

  # Environment variables
  environment_variables = local.environment_variables

  # Policies
  attach_policy_jsons = true
  policy_jsons = [file(local.secrets_manager_policy), file(local.route53_policy)]
  number_of_policy_jsons = 2
}