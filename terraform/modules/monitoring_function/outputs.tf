output "function_name" {
  value       = google_cloudfunctions2_function.monitoring_function.name
  description = "Name of the Cloud Function"
}

output "function_url" {
  value       = google_cloudfunctions2_function.monitoring_function.service_config[0].uri
  description = "URL of the Cloud Function"
}

output "service_account_email" {
  value       = google_service_account.monitoring_function_sa.email
  description = "Email of the monitoring function service account"
}

output "monitoring_bucket_name" {
  value       = google_storage_bucket.monitoring_bucket.name
  description = "Name of the monitoring bucket"
}