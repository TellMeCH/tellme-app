terraform {
  required_version = ">= 1.6.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0"
    }
  }
}

# Create Cloud Storage buckets
resource "google_storage_bucket" "media_bucket" {
  project  = var.project_id
  name     = "${var.project_id}_${var.media_bucket}"
  location = var.region
  uniform_bucket_level_access = false
  public_access_prevention    = "inherited"
  force_destroy               = false
}

resource "google_storage_bucket" "call_processing_bucket" {
  project  = var.project_id
  name     = "${var.project_id}_${var.call_processing_bucket}"
  location = var.region
  uniform_bucket_level_access = false
  public_access_prevention    = "inherited"
  force_destroy               = false
}

# Monitoring function (staging only)
module "monitoring_function" {
  source                  = "../../modules/monitoring_function"
  project_id              = var.project_id
  region                  = var.region
  function_name           = "langfuse-exporter"
  monitoring_bucket_name  = "monitoring_data"
  runtime                 = "python39"
  entry_point             = "main"
  source_bucket           = "gcf-v2-sources-${data.google_project.this.number}-${var.region}"
  source_object           = "function-source.zip"
}

module "api_revision" {
  source                = "../../stacks/api_revision"
  service_name          = var.service_name
  image_url             = "${var.region}-docker.pkg.dev/${var.project_id}/${var.artifact_repo}/${var.service_name}:${github.sha}"
  project_id            = var.project_id
  region                = var.region
  service_account_email = google_service_account.app.email
  cloud_sql             = "${var.project_id}:${var.region}:${var.sql_instance}"
}