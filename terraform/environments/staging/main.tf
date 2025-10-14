terraform {
  required_version = ">= 1.6.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0"
    }
  }
}

module "api_revision" {
  source                = "../../stacks/api_revision"
  service_name          = var.service_name
  image_url             = "${var.region}-docker.pkg.dev/${var.project_id}/${var.artifact_repo}/${var.service_name}:${github.sha}"
  project_id            = var.project_id
  region                = var.region
  service_account_email = "${var.service_name}-account@${var.project_id}.iam.gserviceaccount.com"
  cloud_sql             = "${var.project_id}:${var.region}:${var.sql_instance}"
}