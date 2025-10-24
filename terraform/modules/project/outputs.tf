output "enabled_services" {
  value       = [for s in google_project_service.services : s.service]
  description = "List of enabled services."
}

output "project_id" {
  value       = google_project.this.project_id
  description = "The managed project id."
}

output "project_number" {
  value       = try(google_project.this.number, null)
  description = "Project number (null if using an existing project without import)."
}
