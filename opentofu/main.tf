resource "aws_secretsmanager_secret" "token" {
  name = var.client_id
}

resource "aws_secretsmanager_secret_version" "token" {
  secret_id     = aws_secretsmanager_secret.token.id
  secret_string = var.token
}

module "docker_image" {
	source = "terraform-aws-modules/lambda/aws//modules/docker-build"

    ecr_repo = local.aws_name
	create_ecr_repo = true
    ecr_force_delete = true

	image_tag = data.toml_file.pyproject.content.tool.poetry.version
    platform = "linux/arm64"
	source_path = local.repo_root
	docker_file_path = "container/Dockerfile"
}

module "lambda_function" {
  source = "terraform-aws-modules/lambda/aws"

  # Name and description
  function_name = local.aws_name
  description   = "Simple Dynamic DNS"

  # Function config
  create_package = false
  image_uri = module.docker_image.image_uri
  package_type = "Image"
  architectures = ["arm64"]
  timeout = 5

  # Function URL
  create_lambda_function_url = true
  authorization_type = "NONE"

  # Environment variables
  environment_variables = var.environment_variables

  # Policies
  attach_policy_jsons = true
  policy_jsons = [file(local.secrets_manager_policy), file(local.route53_policy)]
  number_of_policy_jsons = 2
}