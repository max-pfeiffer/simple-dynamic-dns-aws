locals {
  repo_root = "${dirname(abspath(path.root))}"
  docker_context = "${local.repo_root}"
  docker_file = "${local.repo_root}/container/Dockerfile"
}
