/*
Module that bootstraps the app. That is,
1. Creates a GCP project per environment.
2. Creates a unique infra project in GCP.
3. Generates a GCP storage bucket in the infra project that serves as Terraform backend state.
4. Generates a pool and provider for WIF in GCP so we can hook GitHub actions.
5. Defines (but doesn't fill) secrets used in the app.

Note: This module is supposed to be run locally once, on bootstrap, and the output should
      be copied to `backend.tf` inside each env.
*/

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0"
    }
  }
}

# Configure the Google Beta provider with quota project
provider "google-beta" {
  project                 = module.project["infra"].project_id
  billing_project         = module.project["infra"].project_id
  user_project_override   = true
}

# Create a unique, versioned state bucket in the infra project.
resource "random_id" "suffix" {
  byte_length = 6
}

# Create the bucket to hold Terraform state.
resource "google_storage_bucket" "tfstate" {
  project = module.project["infra"].project_id
  name     = "${module.project["infra"].project_id}-${random_id.suffix.hex}-tfstate"
  location = var.region

  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  force_destroy               = false

  versioning {
    enabled = true
  }
}

# Create Workload Identity Federation so GitHub can use GCP for us.
module "wif" {
  source      = "../../modules/wif"
  project_id  = module.project["infra"].project_id
  pool_id     = var.pool_id
  provider_id = var.provider_id
  github_org  = var.github_org
}

# Create a artifact registry repository.
resource "google_artifact_registry_repository" "artifact_repo" {
  for_each = local.sa_envs
  project  = module.project[each.key].project_id
  location = var.region
  repository_id = var.artifact_registry_repository_id
  description   = "Docker repo for backend"
  format        = "DOCKER"
}

# Generate service account key for CICD (needed for Firebase custom tokens)
resource "google_service_account_key" "github_key" {
  for_each           = local.sa_envs
  service_account_id = google_service_account.github[each.key].name
}

# Store the key in the existing secret
resource "google_secret_manager_secret_version" "cicd_service_account_key" {
  for_each    = local.sa_envs
  secret      = "projects/${module.project[each.key].project_id}/secrets/cicd_service_account_key"
  secret_data = base64decode(google_service_account_key.github_key[each.key].private_key)

  depends_on = [module.secrets]
}

# Firebase Authentication configuration for each environment
module "firebase" {
  for_each                    = local.sa_envs
  source                      = "../../modules/firebase"
  project_id                  = module.project[each.key].project_id
  authorized_domains          = var.envs[each.key].authorized_domains
  redirect_uris               = var.envs[each.key].redirect_uris
  homepage_url                = var.homepage_url
  google_oauth_client_id      = var.envs[each.key].google_oauth_client_id
  google_oauth_client_secret  = var.envs[each.key].google_oauth_client_secret

  depends_on = [module.project]
}
