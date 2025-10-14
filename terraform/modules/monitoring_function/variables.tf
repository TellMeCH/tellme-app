variable "project_id" {
  type        = string
  description = "GCP Project ID"
}

variable "region" {
  type        = string
  description = "GCP region"
}

variable "function_name" {
  type        = string
  description = "Name of the Cloud Function"
}

variable "monitoring_bucket_name" {
  type        = string
  description = "Name of the monitoring bucket"
  default     = "monitoring_data"
}

variable "runtime" {
  type        = string
  description = "Runtime for the Cloud Function"
  default     = "python39"
}

variable "entry_point" {
  type        = string
  description = "Entry point for the Cloud Function"
}

variable "build_service_account_email" {
  type        = string
  description = "Service account email for Cloud Function builds (GitHub SA)"
}

variable "repo_name" {
  type        = string
  description = "Cloud Source Repository name"
}

variable "branch_name" {
  type        = string
  description = "Branch name to deploy from"
  default     = "main"
}

variable "source_dir" {
  type        = string
  description = "Directory containing the function source code"
}

variable "max_instance_count" {
  type        = number
  description = "Maximum number of instances"
  default     = 1
}

variable "available_memory" {
  type        = string
  description = "Available memory for the function"
  default     = "256M"
}

variable "timeout_seconds" {
  type        = number
  description = "Function timeout in seconds"
  default     = 60
}

variable "environment_variables" {
  type        = map(string)
  description = "Environment variables for the function"
  default     = {}
}

variable "schedule" {
  type        = string
  description = "Cron schedule for the Cloud Scheduler job"
  default     = "0 */6 * * *"  # Every 6 hours
}

variable "time_zone" {
  type        = string
  description = "Time zone for the scheduler"
  default     = "UTC"
}