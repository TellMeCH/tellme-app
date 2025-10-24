variable "project_id" {
  type        = string
  description = "Unique project ID (globally unique)."
}

variable "name" {
  type        = string
  description = "Project display name."
}

variable "billing_account" {
  type        = string
  description = "Billing account ID."
}

variable "folder_id" {
  type        = string
  description = "Folder to put this project in."
  default     = null
}

variable "org_id" {
  type        = string
  description = "GCP organization to put this project in."
  default     = null
}

variable "environment" {
  type        = string
  description = "Environment label (staging, prod, etc.)."
}

variable "labels" {
  type        = map(string)
  default     = {}
}

variable "services" {
  type        = list(string)
  default     = []
}

