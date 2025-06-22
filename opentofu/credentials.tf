# The API token needs to be URL safe, so we avoid special characters
resource "random_password" "api_token" {
  length  = 10
  special = false
}