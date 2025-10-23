  terraform {
    backend "gcs" {
      bucket = "tellme-app-infra-7eddd32754fb-tfstate"
      prefix = "infra/envs/staging"
    }
  }