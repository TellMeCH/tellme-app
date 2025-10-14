data "google_project" "this" {
  project_id = var.project_id
}

resource "google_cloud_run_v2_service_iam_member" "cloudrun_invoker" {
  project  = var.project_id
  location = var.region
  name     = var.service_name
  role     = "roles/run.invoker"
  member   = "${var.service_name}-account@${var.project_id}.iam.gserviceaccount.com"
}
