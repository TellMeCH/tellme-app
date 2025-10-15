variable "instance_connection_name" {
  description = "Cloud SQL connection name (project:region:instance)"
  type        = string
}

variable "database_name" {
  description = "Database name"
  type        = string
}

variable "admin_username" {
  description = "Admin username for connecting"
  type        = string
}

variable "admin_password" {
  description = "Admin password for connecting"
  type        = string
  sensitive   = true
}

variable "app_username" {
  description = "Application user to create"
  type        = string
}

variable "app_password" {
  description = "Application user password"
  type        = string
  sensitive   = true
}