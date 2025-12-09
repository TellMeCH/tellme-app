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

output "service_account_email" {
  description = "Email of the app service account"
  value       = google_service_account.app.email
}

output "api_gateway_url" {
  description = "The URL of the API Gateway"
  value       = "https://${google_api_gateway_gateway.gateway.default_hostname}"
}

# Load Balancer outputs
output "load_balancer_ip" {
  description = "IP address of the Load Balancer"
  value       = google_compute_global_address.api_ip.address
}

output "load_balancer_url" {
  description = "URL of the Load Balancer"
  value       = "https://${var.api_domain}"
}