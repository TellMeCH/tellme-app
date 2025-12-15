resource "google_cloud_tasks_queue" "call_processing_queue" {
  project  = var.project_id
  name     = var.call_processing_queue_name
  location = var.region

  retry_config {
    max_attempts       = var.max_attempts
    max_retry_duration = var.max_retry_duration
    min_backoff        = var.min_backoff
    max_backoff        = var.max_backoff
    max_doublings      = var.max_doublings
  }

  rate_limits {
    max_concurrent_dispatches = var.max_concurrent_dispatches
    max_concurrent_dispatches = var.max_dispatches_per_second
  }

  stackdriver_logging_config {
    sampling_ratio = var.log_sampling_ratio
  }
}

resource "google_cloud_tasks_queue" "summarization_queue" {
  project  = var.project_id
  name     = var.summarization_queue_name
  location = var.region

  retry_config {
    max_attempts       = var.max_attempts
    max_retry_duration = var.max_retry_duration
    min_backoff        = var.min_backoff
    max_backoff        = var.max_backoff
    max_doublings      = var.max_doublings
  }

  rate_limits {
    max_concurrent_dispatches = var.max_concurrent_dispatches
    max_concurrent_dispatches = var.max_dispatches_per_second
  }

  stackdriver_logging_config {
    sampling_ratio = var.log_sampling_ratio
  }
}