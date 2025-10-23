variable "project_id" { type = string }
variable "region" { type = string }
variable "service_name" { type = string }
variable "sql_instance" { type = string }

variable "github_repo" {
  description = "GitHub repo in the form ORG/REPO"
  type        = string

  validation {
    condition     = can(regex("^[^/]+/[^/]+$", var.github_repo))
    error_message = "github_repo must be in the form ORG/REPO (e.g., my-org/my-repo)."
  }
}

# Bucket names
variable "media_bucket" {
  type = string
  default = "static_files"
}

variable "call_processing_bucket" {
  type = string
  default = "call_recordings"
}

# New variables needed for api_revision stack
variable "image_url" {
  type        = string
  description = "Container image URL with tag/digest"
}

variable "settings_name" {
  type        = string
  description = "Django settings secret name"
  default     = "django_settings"
}

variable "database_name" {
  type        = string
  description = "Database name"
  default     = "db"
}

variable "cloud_tasks_queue_name" {
  type        = string
  description = "Cloud Tasks queue name"
  default     = "call-processing"
}

variable "frontend_path" {
  type        = string
  description = "Frontend path"
  default     = "/static"
}

# CloudSQL credentials
variable "admin_username" {
  type        = string
  description = "CloudSQL admin username"
  default     = "postgres"
}

variable "admin_password" {
  type        = string
  description = "CloudSQL admin password"
  sensitive   = true
}

variable "app_username" {
  type        = string
  description = "CloudSQL app username"
  default     = "app_user"
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