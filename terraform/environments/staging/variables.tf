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

variable "processing_queue_name" {
  type        = string
  description = "Processing queue name"
  default     = "call-processing"
}

variable "summarization_queue_name" {
  type        = string
  description = "Summarization queue name"
  default     = "summarization"
}

variable "tickets_queue_name" {
  type        = string
  description = "Tickets queue name"
  default     = "tickets"
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

# Load Balancer domain
variable "api_domain" {
  type        = string
  description = "Custom domain for the API Load Balancer"
  default     = "test-api.tell-me.ch"
}

# IAP Configuration
variable "iap_client_id" {
  type        = string
  description = "OAuth 2.0 Client ID for IAP"
}

variable "iap_client_secret" {
  type        = string
  description = "OAuth 2.0 Client Secret for IAP"
  sensitive   = true
}

variable "iap_allowed_members" {
  type        = list(string)
  description = "List of members allowed to access /admin through IAP"
}

# Cloudflare Origin Certificate
variable "cf_origin_cert" {
  type        = string
  description = "Cloudflare Origin Certificate (PEM) for the Load Balancer"
}

variable "cf_origin_key" {
  type        = string
  description = "Cloudflare Origin Certificate private key (PEM)"
  sensitive   = true
}