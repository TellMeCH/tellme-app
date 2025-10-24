# Skip "infra".
locals {
  sa_envs = {
    for k, v in var.envs : k => v
    if k != "infra"
  }
}
