# Create a service account to handle the app for each environment.
resource "google_service_account" "app" {
  for_each = local.sa_envs
  project      = module.project[each.key].project_id
  account_id   = "${var.service_name}-account"
  display_name = "tellme App Service Account (${each.value.environment})"
}

resource "google_service_account" "github" {
  for_each = local.sa_envs
  project      = module.project[each.key].project_id
  account_id   = "tell-me-app-cicd"
  display_name = "GitHub Service Account (${each.value.environment})"
}

# Used by GitHub so it can impersonate its service account.
resource "google_service_account_iam_member" "wif_binding" {
  for_each = local.sa_envs
  service_account_id = google_service_account.github[each.key].name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${module.wif.pool_name}/attribute.repository/${var.github_repo}"
}

# Used by Github to be able to sign tokens (needed by Cloud Run)
resource "google_service_account_iam_member" "wif_token_creator" {
  for_each = local.sa_envs
  service_account_id = google_service_account.github[each.key].name
  role               = "roles/iam.serviceAccountTokenCreator"  # TODO: Why is the member not the service account ID?
  member             = "principalSet://iam.googleapis.com/${module.wif.pool_name}/attribute.repository/${var.github_repo}"
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

# Used by the SA account to have access to the bucket holding the Terraform state.
resource "google_storage_bucket_iam_member" "tfstate_object_admin" {
  for_each = local.sa_envs
  bucket = google_storage_bucket.tfstate.id
  role   = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.github[each.key].email}"
}

# Used by the SA account to deploy a Cloud Run revision
resource "google_project_iam_member" "cloud_run_developer" {
  for_each = local.sa_envs
  project = module.project[each.key].project_id
  role    = "roles/run.developer"
  member  = "serviceAccount:${google_service_account.github[each.key].email}"
 }

# Allows GitHub to attach a service account to a resource.
resource "google_project_iam_member" "sa_user" {
  for_each = local.sa_envs

  project = module.project[each.key].project_id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${google_service_account.github[each.key].email}"
}

# TODO: How to mimic this? gcloud iam service-accounts add-iam-policy-binding "${SERVICE_NAME}-account@${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com" \
#    --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${GOOGLE_CLOUD_PROJECT}.iam.gserviceaccount.com" \
#    --role=roles/iam.serviceAccountUser

# TODO: Mismatch with github_authentication.sh
