variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "authorized_domains" {
  description = "List of authorized domains for Firebase Auth"
  type        = list(string)
}

variable "redirect_uris" {
  description = "List of redirect URIs for OAuth providers"
  type        = list(string)
}

variable "support_email" {
  description = "Support email for OAuth brand (required for Google OAuth)"
  type        = string
}

variable "homepage_url" {
  description = "URL of landing page for application"
  type        = string
}

variable "app_name" {
  description = "Display name of application"
  type        = string
}