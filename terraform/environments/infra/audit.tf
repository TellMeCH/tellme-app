# GCP Data Access Audit Logs — enabled for ISO certification
# Covers: invalid access attempts (PERMISSION_DENIED) and system-level activity logs
# Applied to all projects via for_each = var.envs (same pattern as module.project)

# IAM - Admin Read
resource "google_project_iam_audit_config" "iam" {
  for_each = var.envs
  project  = module.project[each.key].project_id
  service  = "iam.googleapis.com"
  audit_log_config { log_type = "ADMIN_READ" }
}

# Resource Manager - Admin Read
resource "google_project_iam_audit_config" "resource_manager" {
  for_each = var.envs
  project  = module.project[each.key].project_id
  service  = "cloudresourcemanager.googleapis.com"
  audit_log_config { log_type = "ADMIN_READ" }
}

# Cloud Storage - Data Read + Data Write
resource "google_project_iam_audit_config" "storage" {
  for_each = var.envs
  project  = module.project[each.key].project_id
  service  = "storage.googleapis.com"
  audit_log_config { log_type = "DATA_READ" }
  audit_log_config { log_type = "DATA_WRITE" }
}

# Compute Engine - Admin Read + Data Write
resource "google_project_iam_audit_config" "compute" {
  for_each = var.envs
  project  = module.project[each.key].project_id
  service  = "compute.googleapis.com"
  audit_log_config { log_type = "ADMIN_READ" }
  audit_log_config { log_type = "DATA_WRITE" }
}

# Cloud KMS - Admin Read + Data Write
resource "google_project_iam_audit_config" "kms" {
  for_each = var.envs
  project  = module.project[each.key].project_id
  service  = "cloudkms.googleapis.com"
  audit_log_config { log_type = "ADMIN_READ" }
  audit_log_config { log_type = "DATA_WRITE" }
}
