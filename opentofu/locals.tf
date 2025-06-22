locals {
  aws_name               = "simple-dyn-dns"
  repo_root              = dirname(abspath(path.root))
  docker_context         = local.repo_root
  docker_file            = "${local.repo_root}/container/Dockerfile"
  pyproject_toml         = "${local.repo_root}/pyproject.toml"
  route53_policy         = "${abspath(path.root)}/route53_policy.json"
  secrets_manager_policy = "${abspath(path.root)}/secrets_manager_policy.json"
}
