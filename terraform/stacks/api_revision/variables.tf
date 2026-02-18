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

variable "gateway_region" {
  type        = string
  description = "API Gateway region (only europe-west1 or europe-west2 supported)"
  default     = "europe-west1"

  validation {
    condition     = contains(["europe-west1", "europe-west2"], var.gateway_region)
    error_message = "Gateway region must be either europe-west1 or europe-west2."
  }
}


variable "min_instance_count" {
  type        = number
  description = "Minimum number of Cloud Run container instances"
}

variable "max_instance_count" {
  type        = number
  description = "Maximum number of Cloud Run container instances"
}

variable "max_concurrent_requests" {
  type        = number
  description = "Maximum number of concurrent requests per Cloud Run instance"
}

variable "instance_memory" {
  type        = string
  description = "Memory of the Cloud Run instance"
}

variable "instance_cpu" {
  type        = string
  description = "CPU of the Cloud Run instance"
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

variable "processing_queue_name" {
  type        = string
  description = "Processing queue name"
}

variable "summarization_queue_name" {
  type        = string
  description = "Summarization queue name"
}

variable "tickets_queue_name" {
  type        = string
  description = "Tickets queue name"
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

# Load Balancer & Security variables
variable "api_domain" {
  type        = string
  description = "Custom domain for the API Load Balancer (e.g., api.yourdomain.com)"
}

variable "availability_type" {
  type        = string
  description = "CloudSQL availability type: ZONAL (single zone) or REGIONAL (high availability)"
  default     = "ZONAL"

  validation {
    condition     = contains(["ZONAL", "REGIONAL"], var.availability_type)
    error_message = "availability_type must be either ZONAL or REGIONAL"
  }
}

variable "activate_alerts" {
  type        = bool
  description = "Enable Cloud SQL storage monitoring alerts"
  default     = false
}

variable "alert_email_addresses" {
  type        = list(string)
  description = "List of email addresses to receive database storage alerts"
  default     = []
}

variable "enable_automated_backups" {
  type        = bool
  description = "Enable automated daily backups for Cloud SQL instance"
  default     = false
}

# IAP Configuration
variable "iap_client_id" {
  type        = string
  description = "OAuth 2.0 Client ID for IAP (created manually in GCP Console)"
}

variable "iap_client_secret" {
  type        = string
  description = "OAuth 2.0 Client Secret for IAP (created manually in GCP Console)"
  sensitive   = true
}

variable "iap_allowed_members" {
  type        = list(string)
  description = "List of members allowed to access /admin through IAP (format: user:email@domain.com or group:group@domain.com)"
}