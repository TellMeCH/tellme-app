terraform {
  backend "gcs" {
    bucket = "tellme-infra-2a3048bca864-tfstate"
    prefix = "infra/envs/infra"
  }
}
