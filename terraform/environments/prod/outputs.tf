output "api_gateway_url" {
  description = "Public API Gateway URL"
  value       = module.api_revision.api_gateway_url
}

output "cloud_run_service_uri" {
  description = "Internal Cloud Run service URI"
  value       = module.api_revision.service_uri
}