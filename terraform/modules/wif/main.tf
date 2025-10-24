resource "google_iam_workload_identity_pool" "pool" {
  project      = var.project_id
  workload_identity_pool_id = var.pool_id
  display_name = "GitHub Actions Pool"
}

resource "google_iam_workload_identity_pool_provider" "provider" {
  project      = var.project_id
  workload_identity_pool_id          = google_iam_workload_identity_pool.pool.workload_identity_pool_id
  workload_identity_pool_provider_id = var.provider_id
  display_name = "My GitHub repo Provider"
  attribute_mapping = {
    "google.subject"                = "assertion.sub"
    "attribute.actor"               = "assertion.actor"
    "attribute.repository"          = "assertion.repository"
    "attribute.repository_id"       = "assertion.repository_id"
    "attribute.repository_owner"    = "assertion.repository_owner"
    "attribute.repository_owner_id" = "assertion.repository_owner_id"
  }
  attribute_condition = "assertion.repository_owner == '${var.github_org}'"
  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}