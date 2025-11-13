output "cloud_run_service_name" {
  description = "Name of the Cloud Run service"
  value       = module.cloud_run_v2.service_name
}

output "service_uri" {
  value       = module.cloud_run_v2.service_uri
  description = "URI of the Cloud Run service"
}

output "cloudsql_connection_name" {
  value       = module.cloudsql.instance_connection_name
  description = "CloudSQL connection name"
}

output "database_name" {
  value       = module.cloudsql.database_name
  description = "Database name"
}

output "media_bucket_name" {
  value       = google_storage_bucket.media_bucket.name
  description = "Media bucket name"
}

output "call_processing_bucket_name" {
  value       = google_storage_bucket.call_processing_bucket.name
  description = "Call processing bucket name"
}

output "call_processing_queue_name" {
  value       = module.tasks.call_processing_queue_name
  description = "Name of the call processing Cloud Tasks queue"
}

output "summarization_queue_name" {
  value       = module.tasks.summarization_queue_name
  description = "Name of the summarization Cloud Tasks queue"
}