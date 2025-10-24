# Ready-to-paste backend snippets (staging/prod use different prefixes)
output "backend_snippet_infra" {
  value = <<EOT
  terraform {
    backend "gcs" {
      bucket = "${google_storage_bucket.tfstate.name}"
      prefix = "infra/envs/infra"
    }
  }
  EOT
}

output "backend_snippet_staging" {
  value = <<EOT
  terraform {
    backend "gcs" {
      bucket = "${google_storage_bucket.tfstate.name}"
      prefix = "infra/envs/staging"
    }
  }
  EOT
}

output "backend_snippet_prod" {
  value = <<EOT
  terraform {
    backend "gcs" {
      bucket = "${google_storage_bucket.tfstate.name}"
      prefix = "infra/envs/prod"
    }
  }
  EOT
}

# Workload Identity Federation provider for GitHub Actions
output "workload_identity_provider" {
  description = "WIF provider for GitHub Actions authentication"
  value       = module.wif.pool_name
}

# CI/CD service account emails by environment
output "cicd_service_accounts" {
  description = "Service account emails for CI/CD by environment"
  value = {
    for env_name, sa in google_service_account.github : env_name => sa.email
  }
}