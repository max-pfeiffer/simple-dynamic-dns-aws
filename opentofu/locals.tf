locals {
  aws_name = "simple-dyn-dns"
  repo_root = "${dirname(abspath(path.root))}"
  docker_context = "${local.repo_root}"
  docker_file = "${local.repo_root}/container/Dockerfile"
  pyproject_toml = "${local.repo_root}/pyproject.toml"
  environment_variables = { for tuple in regexall("(.*)=(.*)", file(".env")) : tuple[0] => tuple[1] }
}
