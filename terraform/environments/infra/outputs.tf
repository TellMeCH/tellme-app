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
  value       = module.wif.provider_name
}

# CI/CD service account emails by environment
output "cicd_service_accounts" {
  description = "Service account emails for CI/CD by environment"
  value = {
    for env_name, sa in google_service_account.github : env_name => sa.email
  }
}

# Drata GRC Integration Outputs
# https://github.com/drata/gcp-terraform-drata-setup/tree/main
# Drata service account JSON key (sensitive, should be rotated regularly, recommended every 90 days)
# When rotating:
# 1. terraform taint google_service_account_key.drata_key
# 2. terraform apply
# 3. terraform output -raw drata_service_account_key > drata-gcp-private-key.json
# 4. Upload new key to Drata
output "drata_service_account_key" {
  description = "Drata service account JSON key (sensitive - extract with: terraform output -raw drata_service_account_key > drata-gcp-private-key.json)"
  value       = base64decode(google_service_account_key.drata_key.private_key)
  sensitive   = true
}

# Drata service account email
output "drata_service_account_email" {
  description = "Drata service account email address"
  value       = google_service_account.drata.email
}