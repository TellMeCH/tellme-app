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

variable "artifact_repo" {
  type = string
  description = "Artifact Registry repository name"
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