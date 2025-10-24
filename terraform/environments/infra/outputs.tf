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