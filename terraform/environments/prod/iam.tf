# Environment-specific IAM resources for prod

# GitHub service account
data "google_service_account" "github" {
  account_id = "tell-me-app-cicd"
  project    = var.project_id
}

