/*
Module in charge of creating a project in GCP per environment.
If no explicit services are passed, we activate the default services.
*/

locals {
  default_services = [
    "run.googleapis.com",
    "serviceusage.googleapis.com",
    "sql-component.googleapis.com",
    "sqladmin.googleapis.com",
    "compute.googleapis.com",
    "cloudbuild.googleapis.com",
    "secretmanager.googleapis.com",
    "artifactregistry.googleapis.com",
    "dlp.googleapis.com",
    "cloudtasks.googleapis.com",
    "cloudscheduler.googleapis.com",
    "cloudfunctions.googleapis.com",
    "aiplatform.googleapis.com",
    "cloudasset.googleapis.com",
    "customsearch.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "iam.googleapis.com",
    "servicecontrol.googleapis.com",
    "firebase.googleapis.com",
    "identitytoolkit.googleapis.com",
    "iap.googleapis.com",
    "apikeys.googleapis.com"
  ]
}


module "project" {
  for_each        = var.envs
  source          = "../../modules/project"
  org_id          = each.value.org_id
  folder_id       = each.value.folder_id
  project_id      = each.value.project_id
  name            = each.value.name
  billing_account = each.value.billing_account
  environment     = each.value.environment
  services        = each.value.services != null ? each.value.services : local.default_services
}
