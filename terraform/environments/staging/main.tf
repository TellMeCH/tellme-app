terraform {
  required_version = ">= 1.6.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0"
    }
  }
}

# Monitoring function (staging only)
module "monitoring_function" {
  source                   = "../../modules/monitoring_function"
  project_id               = var.project_id
  region                   = var.region
  function_name            = "langfuse-exporter"
  monitoring_bucket_name   = "monitoring_data"
  runtime                  = "python312"
  entry_point              = "export_from_langfuse"
  build_service_account_id = data.google_service_account.github.id
  source_dir               = "../../../tellme/jobs/langfuse_exporter"
  settings_name            = var.settings_name
  schedule                 = "0 0 * * *"
  time_zone                = "Etc/UTC"
}

module "api_revision" {
  source                = "../../stacks/api_revision"
  service_name          = var.service_name
  image_url             = var.image_url
  project_id            = var.project_id
  region                = var.region
  min_instance_count    = 0
  max_instance_count    = 10
  tellme_env            = "staging"
  settings_name         = var.settings_name
  sql_instance_name     = var.sql_instance
  database_name         = var.database_name
  media_bucket          = var.media_bucket
  processing_queue_name = var.processing_queue_name
  summarization_queue_name = var.summarization_queue_name
  call_processing_bucket = var.call_processing_bucket
  frontend_path         = var.frontend_path
  admin_username        = var.admin_username
  admin_password        = var.admin_password
  app_username          = var.app_username
  app_password          = var.app_password
  api_domain            = var.api_domain
}