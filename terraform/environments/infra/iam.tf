
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

# Backend Developer role - group access to secrets
resource "google_secret_manager_secret_iam_member" "backend_dev_django_settings" {
  for_each = local.sa_envs
  project = module.project[each.key].project_id
  secret_id = "django_settings"
  role = "roles/secretmanager.secretAccessor"
  member = "group:${var.backend_dev_group}"
  depends_on = [module.secrets]
}

resource "google_secret_manager_secret_iam_member" "backend_dev_firebase_config" {
  for_each = local.sa_envs
  project = module.project[each.key].project_id
  secret_id = "firebase_config"
  role = "roles/secretmanager.secretAccessor"
  member = "group:${var.backend_dev_group}"
  depends_on = [module.secrets]
}
