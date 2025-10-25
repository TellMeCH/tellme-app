# Service account for the monitoring function
resource "google_service_account" "monitoring_function_sa" {
  project      = var.project_id
  account_id   = "${var.function_name}-account"
  display_name = "Monitoring Function Service Account"
}

# Storage bucket for monitoring function data
resource "google_storage_bucket" "monitoring_bucket" {
  project  = var.project_id
  name     = "${var.project_id}_${var.monitoring_bucket_name}"
  location = var.region

  uniform_bucket_level_access = false
  public_access_prevention    = "inherited"
  force_destroy               = false
}

# Cloud Function (Gen2)
resource "google_cloudfunctions2_function" "monitoring_function" {
  project  = var.project_id
  name     = var.function_name
  location = var.region

  build_config {
    runtime               = var.runtime
    entry_point           = var.entry_point
    service_account = var.build_service_account_email
    source {
      repo_source {
        project_id   = var.project_id
        repo_name    = var.repo_name
        branch_name  = var.branch_name
        dir          = var.source_dir
      }
    }
  }

  service_config {
    max_instance_count    = var.max_instance_count
    available_memory      = var.available_memory
    timeout_seconds       = var.timeout_seconds
    service_account_email = google_service_account.monitoring_function_sa.email
    environment_variables = var.environment_variables
  }
}

# IAM bindings for the monitoring function service account

# Secrets access
resource "google_secret_manager_secret_iam_member" "django_settings_access" {
  project   = var.project_id
  secret_id = "django_settings"
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.monitoring_function_sa.email}"
}

# Storage bucket access
resource "google_storage_bucket_iam_member" "monitoring_bucket_access" {
  bucket = google_storage_bucket.monitoring_bucket.name
  role   = "roles/storage.objectUser"
  member = "serviceAccount:${google_service_account.monitoring_function_sa.email}"
}

# Function invoker permissions
resource "google_cloudfunctions2_function_iam_member" "invoker" {
  project        = var.project_id
  location       = var.region
  cloud_function = google_cloudfunctions2_function.monitoring_function.name
  role           = "roles/cloudfunctions.invoker"
  member         = "serviceAccount:${google_service_account.monitoring_function_sa.email}"
}

# Logging permissions
resource "google_project_iam_member" "logging_logwriter" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.monitoring_function_sa.email}"
}

# Cloud Scheduler job to trigger the monitoring function
resource "google_cloud_scheduler_job" "monitoring_scheduler" {
  project     = var.project_id
  name        = "${var.function_name}-scheduler"
  description = "Trigger monitoring function on schedule"
  schedule    = var.schedule
  time_zone   = var.time_zone
  region      = var.region

  http_target {
    http_method = "GET"
    uri         = google_cloudfunctions2_function.monitoring_function.service_config[0].uri
    oidc_token {
      service_account_email = google_service_account.monitoring_function_sa.email
      audience              = google_cloudfunctions2_function.monitoring_function.service_config[0].uri
    }
  }
}