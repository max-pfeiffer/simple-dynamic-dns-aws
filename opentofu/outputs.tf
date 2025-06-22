output "lambda_function_url" {
  value       = module.lambda_function.lambda_function_url
  description = "The URL of the AWS Lambda function."
}

output "api_token" {
  value     = random_password.api_token.result
  sensitive = true
}
