
# Create a service account to authenticate the CICD pipeline
resource "google_service_account" "github" {
  for_each = local.sa_envs
  project      = module.project[each.key].project_id
  account_id   = "tell-me-app-cicd"
  display_name = "GitHub Service Account (${each.value.environment})"
}

# Used by the SA account to push images to the registry.
resource "google_artifact_registry_repository_iam_member" "repo_writer" {
  for_each = local.sa_envs
  project      = module.project[each.key].project_id
  location     = google_artifact_registry_repository.artifact_repo[each.key].location
  repository   = google_artifact_registry_repository.artifact_repo[each.key].repository_id
  role         = "roles/artifactregistry.writer"
  member       = "serviceAccount:${google_service_account.github[each.key].email}"
}

# Used by the SA account to deploy a Cloud Run revision
resource "google_project_iam_member" "cloud_run_developer" {
  for_each = local.sa_envs
  project = module.project[each.key].project_id
  role    = "roles/run.developer"
  member  = "serviceAccount:${google_service_account.github[each.key].email}"
 }

# Cloud SQL client access
resource "google_project_iam_member" "cloudsql_client" {
  for_each = local.sa_envs
  project = module.project[each.key].project_id
  role = "roles/cloudsql.client"
  member = "serviceAccount:${google_service_account.github[each.key].email}"
}

# Allows GitHub to attach a service account to a resource.
resource "google_project_iam_member" "sa_user" {
  for_each = local.sa_envs
  project = module.project[each.key].project_id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${google_service_account.github[each.key].email}"
}

# Used by the SA account to have access to the bucket holding the Terraform state.
resource "google_storage_bucket_iam_member" "tfstate_object_admin" {
  for_each = local.sa_envs
  bucket = google_storage_bucket.tfstate.id
  role   = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.github[each.key].email}"
}

# Firebase auth admin
resource "google_project_iam_member" "firebase_auth_admin" {
  for_each = local.sa_envs
  project = module.project[each.key].project_id
  role = "roles/firebaseauth.admin"
  member = "serviceAccount:${google_service_account.github[each.key].email}"
}

# Cloud Tasks viewer
resource "google_project_iam_member" "cloudtasks_viewer" {
  for_each = local.sa_envs
  project = module.project[each.key].project_id
  role = "roles/cloudtasks.viewer"
  member = "serviceAccount:${google_service_account.github[each.key].email}"
}

# Logging viewer
resource "google_project_iam_member" "logging_viewer" {
  for_each = local.sa_envs
  project = module.project[each.key].project_id
  role = "roles/logging.viewer"
  member = "serviceAccount:${google_service_account.github[each.key].email}"
}

# Used by Github to be able to sign tokens (needed by Cloud Run)
resource "google_project_iam_member" "github_token_creator" {
  for_each = local.sa_envs
  project = module.project[each.key].project_id
  role = "roles/iam.serviceAccountTokenCreator"
  member = "serviceAccount:${google_service_account.github[each.key].email}"
}

# Used by GitHub so it can impersonate its service account.
resource "google_service_account_iam_member" "wif_binding" {
  for_each = local.sa_envs
  service_account_id = google_service_account.github[each.key].name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${module.wif.pool_name}/attribute.repository/${var.github_repo}"
}

# Logging log writer
resource "google_project_iam_member" "logging_logwriter" {
  for_each = local.sa_envs
  project = module.project[each.key].project_id
  role = "roles/logging.logWriter"
  member = "serviceAccount:${google_service_account.github[each.key].email}"
}

# Cloud Scheduler admin
resource "google_project_iam_member" "cloudscheduler_admin" {
  for_each = local.sa_envs
  project = module.project[each.key].project_id
  role = "roles/cloudscheduler.admin"
  member = "serviceAccount:${google_service_account.github[each.key].email}"
}

# API Key Admin
resource "google_project_iam_member" "api_keys_admin" {
  for_each = local.sa_envs
  project = module.project[each.key].project_id
  role    = "roles/serviceusage.apiKeysAdmin"
  member  = "serviceAccount:${google_service_account.github[each.key].email}"
}

# Minimal permissions for service account creation
resource "google_project_iam_member" "service_account_creator" {
  for_each = local.sa_envs
  project = module.project[each.key].project_id
  role    = "roles/iam.serviceAccountCreator"
  member  = "serviceAccount:${google_service_account.github[each.key].email}"
}

# Storage Object Admin (for bucket creation and management)
resource "google_project_iam_member" "storage_object_admin" {
  for_each = local.sa_envs
  project = module.project[each.key].project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.github[each.key].email}"
}

# Storage bucket creator
resource "google_project_iam_member" "storage_bucket_creator" {
  for_each = local.sa_envs
  project = module.project[each.key].project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.github[each.key].email}"
}

# Cloud SQL Admin (for creating instances)
resource "google_project_iam_member" "cloudsql_admin_permission" {
  for_each = local.sa_envs
  project = module.project[each.key].project_id
  role    = "roles/cloudsql.admin"
  member  = "serviceAccount:${google_service_account.github[each.key].email}"
}

# Cloud Tasks Admin (for creating queues)
resource "google_project_iam_member" "cloudtasks_admin_permission" {
  for_each = local.sa_envs
  project = module.project[each.key].project_id
  role    = "roles/cloudtasks.admin"
  member  = "serviceAccount:${google_service_account.github[each.key].email}"
}

# Cloud Functions Developer (for creating functions)
resource "google_project_iam_member" "cloudfunctions_developer" {
  for_each = local.sa_envs
  project = module.project[each.key].project_id
  role    = "roles/cloudfunctions.developer"
  member  = "serviceAccount:${google_service_account.github[each.key].email}"
}

# Security Admin (for IAM policy management on specific resources)
resource "google_project_iam_member" "security_admin" {
  for_each = local.sa_envs
  project = module.project[each.key].project_id
  role    = "roles/iam.securityAdmin"
  member  = "serviceAccount:${google_service_account.github[each.key].email}"
}

# Cloud Build Service Account (still needed for Cloud Functions builds even with storage_source)
resource "google_project_iam_member" "cloudbuild_service_account" {
  for_each = local.sa_envs
  project = module.project[each.key].project_id
  role    = "roles/cloudbuild.builds.builder"
  member  = "serviceAccount:${google_service_account.github[each.key].email}"
}

# Backend Developer role - group access to secrets
resource "google_secret_manager_secret_iam_member" "backend_dev_django_settings" {
  for_each = local.sa_envs
  project = module.project[each.key].project_id
  secret_id = "django_settings"
  role = "roles/secretmanager.secretAccessor"
  member = "group:${var.backend_dev_group}"
  depends_on = [module.secrets]
}

# Load Balancer and Cloud Armour permissions
resource "google_project_iam_member" "compute_security_admin" {
  for_each = local.sa_envs
  project = module.project[each.key].project_id
  role    = "roles/compute.securityAdmin"
  member  = "serviceAccount:${google_service_account.github[each.key].email}"
}

# Load Balancer admin (for SSL certs, URL maps, forwarding rules, etc.)
resource "google_project_iam_member" "compute_load_balancer_admin" {
  for_each = local.sa_envs
  project = module.project[each.key].project_id
  role    = "roles/compute.loadBalancerAdmin"
  member  = "serviceAccount:${google_service_account.github[each.key].email}"
}

# Network endpoint groups admin
resource "google_project_iam_member" "compute_network_admin" {
  for_each = local.sa_envs
  project = module.project[each.key].project_id
  role    = "roles/compute.networkAdmin"
  member  = "serviceAccount:${google_service_account.github[each.key].email}"
}

# API Gateway admin
resource "google_project_iam_member" "apigateway_admin" {
  for_each = local.sa_envs
  project = module.project[each.key].project_id
  role    = "roles/apigateway.admin"
  member  = "serviceAccount:${google_service_account.github[each.key].email}"
}

# Drata GRC Integration
# Get organization data for Drata
data "google_organization" "drata" {
  domain = "tell-me.ch"
}

# Create project-level custom role for Drata
resource "google_project_iam_custom_role" "drata_project_role" {
  project     = module.project["infra"].project_id
  role_id     = "DrataReadOnlyProjectRole"
  title       = "Drata Read-Only Project Role"
  description = "Service Account for Drata Autopilot with read access to project resources"
  permissions = [
    "storage.buckets.get",
    "storage.buckets.getIamPolicy"
  ]
}

# Create organization-level custom role for Drata
resource "google_organization_iam_custom_role" "drata_org_role" {
  org_id      = data.google_organization.drata.org_id
  role_id     = "DrataReadOnlyOrganizationalRole"
  title       = "Drata Read-Only Organizational Role"
  description = "Service Account with read-only access for Drata to scan organizational resources"
  permissions = [
    "resourcemanager.organizations.getIamPolicy",
    "storage.buckets.get",
    "storage.buckets.getIamPolicy",
    "resourcemanager.folders.get",
    "resourcemanager.organizations.get",
    "cloudasset.assets.searchAllResources"
  ]
}

# Create the Drata service account
resource "google_service_account" "drata" {
  project      = module.project["infra"].project_id
  account_id   = "dratareadonly"
  display_name = "Drata Read-Only Scanner"
  description  = "Service account for Drata GRC platform to scan organization resources"
}

# Create JSON key for the Drata service account
resource "google_service_account_key" "drata_key" {
  service_account_id = google_service_account.drata.id
}

# Grant project custom role to Drata
resource "google_project_iam_member" "drata_project_custom" {
  project = module.project["infra"].project_id
  role    = google_project_iam_custom_role.drata_project_role.name
  member  = "serviceAccount:${google_service_account.drata.email}"
}

# Grant organization custom role to Drata
resource "google_organization_iam_member" "drata_org_custom" {
  org_id = data.google_organization.drata.org_id
  role   = google_organization_iam_custom_role.drata_org_role.name
  member = "serviceAccount:${google_service_account.drata.email}"
}

# Grant project viewer role to Drata
resource "google_project_iam_member" "drata_project_viewer" {
  project = module.project["infra"].project_id
  role    = "roles/viewer"
  member  = "serviceAccount:${google_service_account.drata.email}"
}

# Grant organization viewer role to Drata (for multi-project scanning)
resource "google_organization_iam_member" "drata_org_viewer" {
  org_id = data.google_organization.drata.org_id
  role   = "roles/viewer"
  member = "serviceAccount:${google_service_account.drata.email}"
}

# Vanta GRC Integration
# Create custom organization role for Vanta
resource "google_organization_iam_custom_role" "vanta_scanner" {
  org_id      = data.google_organization.drata.org_id
  role_id     = "VantaExtensiveOrganizationScanner"
  title       = "Vanta Extensive Organization Scanner"
  description = "Role for Vanta to scan organization resources and IAM policies"
  permissions = [
    "essentialcontacts.contacts.list",
    "iam.roles.list",
    "resourcemanager.organizations.getIamPolicy",
    "resourcemanager.folders.getIamPolicy",
    "resourcemanager.projects.get",
    "resourcemanager.projects.list",
    "resourcemanager.folders.list",
    "bigquery.datasets.get",
    "compute.instances.get",
    "compute.instances.getEffectiveFirewalls",
    "compute.subnetworks.get",
    "pubsub.topics.get",
    "storage.buckets.get",
    "cloudasset.assets.searchAllResources"
  ]
}

# Workload Identity Federation configuration for Vanta
locals {
  vanta_aws_account_id   = "850507053895"
  vanta_aws_role_name    = "scanner"
  vanta_identity_pool_id = "vanta-3723b513304f983"
  vanta_provider_id      = "vanta-aws"
  vanta_subject_name     = "vanta-scanner"
  # Subject URI references the infra project
  vanta_subject_uri      = "principal://iam.googleapis.com/projects/${module.project["infra"].project_number}/locations/global/workloadIdentityPools/${local.vanta_identity_pool_id}/subject/${local.vanta_subject_name}"
}

# Create Workload Identity Pool in infra project for Vanta
resource "google_iam_workload_identity_pool" "vanta" {
  project                   = module.project["infra"].project_id
  workload_identity_pool_id = local.vanta_identity_pool_id
  display_name              = "Vanta GRC Scanner"
  description               = "Workload Identity Pool for Vanta to scan organization"
}

resource "time_sleep" "wait_vanta_pool" {
  create_duration = "30s"
  depends_on      = [google_iam_workload_identity_pool.vanta]

  lifecycle {
    replace_triggered_by = [
      google_iam_workload_identity_pool.vanta
    ]
  }
}

# Create Workload Identity Provider (AWS federation) for Vanta
resource "google_iam_workload_identity_pool_provider" "vanta_aws" {
  depends_on                         = [time_sleep.wait_vanta_pool]
  project                            = module.project["infra"].project_id
  workload_identity_pool_id          = google_iam_workload_identity_pool.vanta.workload_identity_pool_id
  workload_identity_pool_provider_id = local.vanta_provider_id
  display_name                       = "Vanta AWS"
  description                        = "Allows Vanta's AWS infrastructure to authenticate to GCP"

  attribute_mapping = {
    "google.subject"  = "'${local.vanta_subject_name}'"
    "attribute.arn"   = "assertion.arn"
  }

  attribute_condition = "attribute.arn.extract('assumed-role/{role}/') == '${local.vanta_aws_role_name}'"

  aws {
    account_id = local.vanta_aws_account_id
  }
}

# Grant custom scanner role at organization level to Vanta
resource "google_organization_iam_member" "vanta_custom_role" {
  depends_on = [google_iam_workload_identity_pool_provider.vanta_aws]
  org_id     = data.google_organization.drata.org_id
  role       = google_organization_iam_custom_role.vanta_scanner.name
  member     = local.vanta_subject_uri
}

# Grant security reviewer role at organization level to Vanta
resource "google_organization_iam_member" "vanta_security_reviewer" {
  depends_on = [google_iam_workload_identity_pool_provider.vanta_aws]
  org_id     = data.google_organization.drata.org_id
  role       = "roles/iam.securityReviewer"
  member     = local.vanta_subject_uri
}

# Wait for IAM propagation for Vanta
resource "time_sleep" "wait_vanta_iam" {
  create_duration = "60s"
  depends_on = [
    google_organization_iam_member.vanta_custom_role,
    google_organization_iam_member.vanta_security_reviewer,
  ]

  lifecycle {
    replace_triggered_by = [
      google_organization_iam_member.vanta_custom_role,
      google_organization_iam_member.vanta_security_reviewer,
    ]
  }
}
