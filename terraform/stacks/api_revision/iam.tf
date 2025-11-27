# Create the app service account
resource "google_service_account" "app" {
  project      = var.project_id
  account_id   = "${var.service_name}-account"
  display_name = "tellme App Service Account"

  lifecycle {
    prevent_destroy = true
  }
}

# Cloud Run invoker for allUsers (public access)
resource "google_cloud_run_v2_service_iam_member" "cloudrun_invoker_public" {
  project  = var.project_id
  location = var.region
  name     = var.service_name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Runtime service account IAM bindings

# Cloud SQL client access
resource "google_project_iam_member" "runtime_cloudsql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.app.email}"
}

# Storage bucket access for media files
resource "google_storage_bucket_iam_member" "runtime_media_bucket" {
  bucket = google_storage_bucket.media_bucket.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.app.email}"
}

# Storage bucket access for call recordings (objectUser for runtime)
resource "google_storage_bucket_iam_member" "runtime_call_processing_bucket" {
  bucket = google_storage_bucket.call_processing_bucket.name
  role   = "roles/storage.objectUser"
  member = "serviceAccount:${google_service_account.app.email}"
}

# Secrets access
resource "google_secret_manager_secret_iam_member" "runtime_django_settings" {
  project   = var.project_id
  secret_id = "django_settings"
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.app.email}"
}

# Firebase auth admin
resource "google_project_iam_member" "runtime_firebase_auth_admin" {
  project = var.project_id
  role    = "roles/firebaseauth.admin"
  member  = "serviceAccount:${google_service_account.app.email}"
}

# Cloud Tasks enqueuer
resource "google_project_iam_member" "runtime_cloudtasks_enqueuer" {
  project = var.project_id
  role    = "roles/cloudtasks.enqueuer"
  member  = "serviceAccount:${google_service_account.app.email}"
}

# Cloud Tasks viewer
resource "google_project_iam_member" "runtime_cloudtasks_viewer" {
  project = var.project_id
  role    = "roles/cloudtasks.viewer"
  member  = "serviceAccount:${google_service_account.app.email}"
}

# DLP user
resource "google_project_iam_member" "runtime_dlp_user" {
  project = var.project_id
  role    = "roles/dlp.user"
  member  = "serviceAccount:${google_service_account.app.email}"
}

# Service usage consumer
resource "google_project_iam_member" "runtime_serviceusage_consumer" {
  project = var.project_id
  role    = "roles/serviceusage.serviceUsageConsumer"
  member  = "serviceAccount:${google_service_account.app.email}"
}

# AI Platform user
resource "google_project_iam_member" "runtime_aiplatform_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.app.email}"
}

# GitHub service account access
data "google_service_account" "github" {
  account_id = "tell-me-app-cicd"
  project    = var.project_id
}

# Allow GitHub service account to use the app service account
resource "google_service_account_iam_member" "github_app_sa_user" {
  service_account_id = google_service_account.app.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${data.google_service_account.github.email}"
}

# GitHub access to media bucket
resource "google_storage_bucket_iam_member" "github_media_bucket" {
  bucket = google_storage_bucket.media_bucket.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${data.google_service_account.github.email}"
}

# GitHub access to call processing bucket
resource "google_storage_bucket_iam_member" "github_call_processing_bucket" {
  bucket = google_storage_bucket.call_processing_bucket.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${data.google_service_account.github.email}"
}

# GitHub access to API Gateway
resource "google_project_iam_member" "gw_admin" {
  project = var.project_id
  role    = "roles/apigateway.admin"
  member  = "serviceAccount:${data.google_service_account.github.email}"
}

