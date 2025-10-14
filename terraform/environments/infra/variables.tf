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
    org_id          = optional(string)
    project_id      = string
    name            = string
    environment     = string
    billing_account = string
    folder_id       = optional(string)
    services        = optional(set(string))
  }))
}

variable "service_name" { type = string }
