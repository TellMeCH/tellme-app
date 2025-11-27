# Environment-specific IAM resources for staging

# GitHub service account
data "google_service_account" "github" {
  account_id = "tell-me-app-cicd"
  project    = var.project_id
}

# Monitoring Function GitHub IAM bindings
# Allow GitHub to use monitoring function service account
resource "google_service_account_iam_member" "github_monitoring_sa_user" {
  service_account_id = module.monitoring_function.service_account_name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${data.google_service_account.github.email}"
}
