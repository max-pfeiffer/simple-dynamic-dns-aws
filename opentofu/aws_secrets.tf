resource "aws_secretsmanager_secret" "token" {
  name = var.client_id
}

resource "aws_secretsmanager_secret_version" "token" {
  secret_id     = aws_secretsmanager_secret.token.id
  secret_string = random_password.api_token.result
}
