output "api_gateway_url" {
  description = "Public API Gateway URL"
  value       = module.api_revision.api_gateway_url
}

output "cloud_run_service_uri" {
  description = "Internal Cloud Run service URI"
  value       = module.api_revision.service_uri
}

# Load Balancer outputs
output "load_balancer_ip" {
  description = "IP address of the Load Balancer"
  value       = module.api_revision.load_balancer_ip
}

output "load_balancer_url" {
  description = "URL of the Load Balancer (primary entry point)"
  value       = module.api_revision.load_balancer_url
}