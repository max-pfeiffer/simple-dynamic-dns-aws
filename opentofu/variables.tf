variable "client_id" {
  type      = string
  sensitive = true
}

variable "environment_variables" {
  type      = map(string)
  sensitive = false
}

