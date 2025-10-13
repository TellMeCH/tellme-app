variable "google_cloud_project" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region"
  type        = string
  default     = "europe-west6"
}

variable "environment" {
  description = "Environment name (staging or prod)"
  type        = string
  validation {
    condition     = contains(["staging", "prod"], var.environment)
    error_message = "Environment must be either 'staging' or 'prod'."
  }
}

variable "service_name" {
  description = "Base service name"
  type        = string
}

variable "sql_instance_name" {
  description = "Cloud SQL instance name"
  type        = string
}

variable "database_name" {
  description = "Database name"
  type        = string
}

variable "media_bucket_suffix" {
  description = "Media bucket suffix"
  type        = string
}

variable "call_processing_bucket_suffix" {
  description = "Call processing bucket suffix"
  type        = string
}

variable "monitoring_bucket_suffix" {
  description = "Monitoring bucket suffix (staging only)"
  type        = string
  default     = ""
}

variable "cloud_tasks_queue_name" {
  description = "Cloud Tasks queue name"
  type        = string
}

variable "artifact_repo" {
  description = "Artifact repository name"
  type        = string
}

variable "monitoring_function" {
  description = "Monitoring function name (staging only)"
  type        = string
  default     = ""
}

variable "workload_identity_provider" {
  description = "Workload identity provider for GitHub Actions"
  type        = string
}

variable "cicd_service_account" {
  description = "CI/CD service account email"
  type        = string
}