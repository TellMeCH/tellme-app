variable "project_id" {
  type        = string
  description = "GCP Project ID"
}

variable "region" {
  type        = string
  description = "GCP region"
}

variable "instance_name" {
  type        = string
  description = "Name of the Cloud SQL instance"
}

variable "tier" {
  type        = string
  description = "Machine type tier for the instance"
  default     = "db-custom-1-3840"
}

variable "database_name" {
  type        = string
  description = "Name of the database"
}

variable "admin_username" {
  type        = string
  description = "Admin username for the database"
}

variable "admin_password" {
  type        = string
  description = "Admin password for the database"
  sensitive   = true
}

variable "app_username" {
  type        = string
  description = "Application username for the database"
}

variable "app_password" {
  type        = string
  description = "Application password for the database"
  sensitive   = true
}

variable "deletion_protection" {
  type        = bool
  description = "Whether to enable deletion protection"
  default     = true
}

variable "availability_type" {
  type        = string
  description = "Availability type for Cloud SQL instance. ZONAL (single zone) or REGIONAL (high availability with automatic failover)"
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

variable "tellme_env" {
  type        = string
  description = "Environment name (dev/staging/prod). Used to gate prod-only resources such as Backup DR."
}

