output "cloud_run_service_name" {
  description = "Name of the Cloud Run service"
  value       = module.cloud_run_v2.service_name
}

output "cloud_run_service_uri" {
  description = "Fully qualified URI of the Cloud Run service"
  value       = module.cloud_run_v2.service_uri
}