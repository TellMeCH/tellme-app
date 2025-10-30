variable "project_id" {
  type        = string
  description = "GCP Project ID"
}

variable "region" {
  type        = string
  description = "GCP region"
}

variable "call_processing_queue_name" {
  type        = string
  description = "Name of the call processing Cloud Tasks queue"
}

variable "summarization_queue_name" {
  type        = string
  description = "Name of the summarization Cloud Tasks queue"
}

variable "max_attempts" {
  type        = number
  description = "Maximum number of retry attempts"
  default     = 2
}

variable "max_retry_duration" {
  type        = string
  description = "Maximum retry duration"
  default     = "3600s"
}

variable "min_backoff" {
  type        = string
  description = "Minimum backoff duration"
  default     = "20s"
}

variable "max_backoff" {
  type        = string
  description = "Maximum backoff duration"
  default     = "80s"
}

variable "max_doublings" {
  type        = number
  description = "Maximum number of doublings"
  default     = 3
}

variable "max_concurrent_dispatches" {
  type        = number
  description = "Maximum concurrent dispatches"
  default     = 10
}

variable "log_sampling_ratio" {
  type        = number
  description = "Log sampling ratio"
  default     = 1.0
}