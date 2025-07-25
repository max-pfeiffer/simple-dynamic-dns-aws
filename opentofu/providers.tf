data "aws_region" "current" {}

data "aws_caller_identity" "this" {}

data "aws_ecr_authorization_token" "token" {}

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.0.0"
    }
    docker = {
      source  = "kreuzwerker/docker"
      version = "3.6.2"
    }
    toml = {
      source  = "tobotimus/toml"
      version = "0.3.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "3.7.1"
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

