variable "folder_id" {
  description = "Numeric folder ID to place the infra project under."
  type        = string
  default     = null
}

variable "billing_account" {
  description = "Billing account ID, e.g. 000000-AAAAAA-BBBBBB"
  type        = string
}

variable "region" {
  description = "Region for the state bucket."
  type        = string
}

# WIF
variable "provider_id" { type = string }

variable "pool_id" { type = string }

variable "github_repo" {
  description = "GitHub repo in the form ORG/REPO"
  type        = string

  validation {
    condition     = can(regex("^[^/]+/[^/]+$", var.github_repo))
    error_message = "github_repo must be in the form ORG/REPO (e.g., my-org/my-repo)."
  }
}

variable "artifact_registry_repository_id" { type = string }


variable "envs" {
  description = "Per-environment config"
  type = map(object({
    org_id                     = optional(string)
    project_id                 = string
    name                       = string
    environment                = string
    billing_account            = string
    folder_id                  = optional(string)
    services                   = optional(set(string))
    authorized_domains         = optional(list(string))
    redirect_uris              = optional(list(string))
    google_oauth_client_id     = optional(string)
    google_oauth_client_secret = optional(string)
    labels                     = optional(map(string))
  }))
}


# GitHub organization for WIF
variable "github_org" {
  type = string
  description = "GitHub organization name for WIF provider"
}

variable "backend_dev_group" {
  type = string
  description = "Google Group for backend developers"
}

variable "homepage_url" {
  description = "URL of landing page for application"
  type        = string
}