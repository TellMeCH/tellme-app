variable "service_name" {
  type        = string
  description = "Name of the Cloud Run service"
}

variable "image_url" {
  type        = string
  description = "Container image URL"
}

variable "project_id" {
  type        = string
  description = "GCP Project ID"
}

variable "region" {
  type        = string
  description = "GCP region"
}

variable "service_account_email" {
  type        = string
  description = "Service account email for Cloud Run"
}


variable "tellme_env" {
  type        = string
  description = "Environment (staging/prod)"
}

variable "settings_name" {
  type        = string
  description = "Django settings name"
}

variable "sql_instance_name" {
  type        = string
  description = "SQL instance name"
}

variable "database_name" {
  type        = string
  description = "Database name"
}

variable "media_bucket" {
  type        = string
  description = "Media bucket name"
}

variable "cloud_tasks_queue_name" {
  type        = string
  description = "Cloud Tasks queue name"
}

variable "call_processing_bucket" {
  type        = string
  description = "Call processing bucket name"
}

variable "frontend_path" {
  type        = string
  description = "Frontend path"
}

# CloudSQL variables
variable "admin_username" {
  type        = string
  description = "CloudSQL admin username"
}

variable "admin_password" {
  type        = string
  description = "CloudSQL admin password"
  sensitive   = true
}

variable "app_username" {
  type        = string
  description = "CloudSQL app username"
}

variable "app_password" {
  type        = string
  description = "CloudSQL app password"
  sensitive   = true
}

variable "create_app_user" {
  type        = number
  description = "Whether to create the application database user (0 = false, 1 = true)"
  default     = 1

  validation {
    condition     = var.create_app_user == 0 || var.create_app_user == 1
    error_message = "create_app_user must be either 0 (false) or 1 (true)."
  }
}