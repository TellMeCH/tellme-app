terraform {
  required_version = ">= 1.6.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0"
    }
  }
}

# Tell Terraform that the service account moved from here to the api_revision module
moved {
  from = google_service_account.app
  to   = module.api_revision.google_service_account.app
}

# Tell Terraform that the API Gateway IAM binding is now managed by infra environment
# This prevents Terraform from destroying it in GCP when removing it from this state
# You can remove this block after successfully running terraform apply
removed {
  from = module.api_revision.google_project_iam_member.gw_admin

  lifecycle {
    destroy = false
  }
}

module "api_revision" {
  source                = "../../stacks/api_revision"
  service_name          = var.service_name
  image_url             = var.image_url
  project_id            = var.project_id
  region                = var.region
  min_instance_count    = 2
  max_instance_count    = 20
  tellme_env            = "prod"
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