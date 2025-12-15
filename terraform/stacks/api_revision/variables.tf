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
  default     = 10  # Cloud Run default, reasonable for most workloads
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