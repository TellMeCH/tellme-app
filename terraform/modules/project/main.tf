/*
Module that generates a GCP project in the correct folder linked to a billing account.
Also enables the APIs delimited by the variable `services`.
*/

# Create project
resource "google_project" "this" {
  project_id      = var.project_id
  name            = var.name
  billing_account = var.billing_account
  folder_id       = var.folder_id
  org_id          = var.org_id
  deletion_policy = "DELETE"

  labels = merge(
    {
      environment = var.environment
      managed_by  = "terraform"
    },
    var.labels
  )

  lifecycle {
    precondition {
      condition     = (var.folder_id == null) != (var.org_id == null)
      error_message = "Set exactly one of folder_id or org_id."
    }
  }

}

# Enable APIs
resource "google_project_service" "services" {
  for_each = toset(var.services)
  project  = google_project.this.project_id
  service  = each.value

  disable_on_destroy = false
}
