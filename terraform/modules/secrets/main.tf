# Step 1: enable Secret Manager API.
resource "google_project_service" "secretmanager" {
  project = var.project_id
  service = "secretmanager.googleapis.com"
  disable_on_destroy = false
}

# Step 2: create all secrets.
resource "google_secret_manager_secret" "secrets" {
  for_each = toset(var.secret_ids)
  project   = var.project_id
  secret_id = each.key
  replication {
    auto {}
  }
  depends_on = [google_project_service.secretmanager]
}

# Step 3: grant runtime service account read access to each secret.
resource "google_secret_manager_secret_iam_member" "access" {
  for_each = google_secret_manager_secret.secrets
  project   = var.project_id
  secret_id = each.value.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${var.runtime_sa_email}"
}
