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

variable "homepage_url" {
  description = "URL of landing page for application"
  type        = string
}

variable "google_oauth_client_id" {
  description = "Google OAuth client ID (manually created in Google Cloud Console)"
  type        = string
}

variable "google_oauth_client_secret" {
  description = "Google OAuth client secret (manually created in Google Cloud Console)"
  type        = string
  sensitive   = true
}