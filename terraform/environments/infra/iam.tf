# Create a service account to handle the app for each environment.
resource "google_service_account" "app" {
  for_each = local.sa_envs
  project      = module.project[each.key].project_id
  account_id   = "${var.service_name}-account"
  display_name = "tellme App Service Account (${each.value.environment})"
}

# Create a service account to authenticate the CICD pipeline
resource "google_service_account" "github" {
  for_each = local.sa_envs
  project      = module.project[each.key].project_id
  account_id   = "tell-me-app-cicd"
  display_name = "GitHub Service Account (${each.value.environment})"
}

# Access to secrets
resource "google_secret_manager_secret_iam_member" "django_settings_access" {
  for_each = local.sa_envs
  project = module.project[each.key].project_id
  secret_id = "django_settings"
  role = "roles/secretmanager.secretAccessor"
  member = "serviceAccount:${google_service_account.github[each.key].email}"
  depends_on = [module.secrets]
}

resource "google_secret_manager_secret_iam_member" "superuser_passwords_access" {
  for_each = local.sa_envs
  project = module.project[each.key].project_id
  secret_id = "superuser_passwords"
  role = "roles/secretmanager.secretAccessor"
  member = "serviceAccount:${google_service_account.github[each.key].email}"
  depends_on = [module.secrets]
}

resource "google_secret_manager_secret_iam_member" "firebase_config_access" {
  for_each = local.sa_envs
  project = module.project[each.key].project_id
  secret_id = "firebase_config"
  role = "roles/secretmanager.secretAccessor"
  member = "serviceAccount:${google_service_account.github[each.key].email}"
  depends_on = [module.secrets]
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

# TODO: What's the difference between these two?
# Allows GitHub to attach a service account to a resource.
resource "google_project_iam_member" "sa_user" {
  for_each = local.sa_envs
  project = module.project[each.key].project_id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${google_service_account.github[each.key].email}"
}
# Allow GitHub service account to use the app service account
resource "google_service_account_iam_member" "github_app_sa_user" {
  for_each = local.sa_envs
  service_account_id = google_service_account.app[each.key].name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.github[each.key].email}"
}

# TODO: What happened to the media bucket access? And the call processing bucket? Should they be defined here?
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

# Monitoring Function IAM bindings (staging only)
# Cloud Functions admin
resource "google_project_iam_member" "cloudfunctions_admin" {
  for_each = {
    for k, v in local.sa_envs : k => v
    if k == "staging"
  }
  project = module.project[each.key].project_id
  role = "roles/cloudfunctions.admin"
  member = "serviceAccount:${google_service_account.github[each.key].email}"
}

# TODO: Where is the monitoring function SA created?
# Allow GitHub to use monitoring function service account
resource "google_service_account_iam_member" "github_monitoring_sa_user" {
  for_each = {
    for k, v in local.sa_envs : k => v
    if k == "staging"
  }
  service_account_id = "${var.monitoring_function_name}-account@${module.project[each.key].project_id}.iam.gserviceaccount.com"
  role = "roles/iam.serviceAccountUser"
  member = "serviceAccount:${google_service_account.github[each.key].email}"
}

# Access to GCF v2 sources bucket (project-specific)
data "google_project" "projects" {
  for_each = {
    for k, v in local.sa_envs : k => v
    if k == "staging"
  }
  project_id = module.project[each.key].project_id
}

resource "google_storage_bucket_iam_member" "gcf_sources_bucket_access" {
  for_each = {
    for k, v in local.sa_envs : k => v
    if k == "staging"
  }
  bucket = "gcf-v2-sources-${data.google_project.projects[each.key].number}-${var.region}"
  role = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.github[each.key].email}"
}

# Logging log writer
resource "google_project_iam_member" "logging_logwriter" {
  for_each = local.sa_envs
  project = module.project[each.key].project_id
  role = "roles/logging.logWriter"
  member = "serviceAccount:${google_service_account.github[each.key].email}"
}

# Functions artifacts repository access
resource "google_artifact_registry_repository_iam_member" "functions_artifacts_writer" {
  for_each = {
    for k, v in local.sa_envs : k => v
    if k == "staging"
  }
  project = module.project[each.key].project_id
  location = var.region
  repository = var.functions_artifacts_repo
  role = "roles/artifactregistry.writer"
  member = "serviceAccount:${google_service_account.github[each.key].email}"
}

# Cloud Scheduler admin
resource "google_project_iam_member" "cloudscheduler_admin" {
  for_each = local.sa_envs
  project = module.project[each.key].project_id
  role = "roles/cloudscheduler.admin"
  member = "serviceAccount:${google_service_account.github[each.key].email}"
}

# TODO: Where is the group created?
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
