# Storage buckets
resource "google_storage_bucket" "media_bucket" {
  project  = var.project_id
  name     = "${var.project_id}_${var.media_bucket}"
  location = var.region
  uniform_bucket_level_access = false
  public_access_prevention    = "inherited"
  force_destroy               = false
}

resource "google_storage_bucket" "call_processing_bucket" {
  project  = var.project_id
  name     = "${var.project_id}_${var.call_processing_bucket}"
  location = var.region
  uniform_bucket_level_access = false
  public_access_prevention    = "inherited"
  force_destroy               = false
}

# Search API Key
resource "google_apikeys_key" "custom_search_key" {
  name    = "revenue-at-stake-search-api-key"
  display_name    = "revenue_at_stake_search_api_key"
  project = var.project_id

  restrictions {
    api_targets {
      service = "customsearch.googleapis.com"
    }
  }
}

# CloudSQL module
module "cloudsql" {
  source          = "../../modules/cloudsql"
  project_id      = var.project_id
  region          = var.region
  instance_name   = var.sql_instance_name
  database_name   = var.database_name
  admin_username  = var.admin_username
  admin_password  = var.admin_password
  app_username    = var.app_username
  app_password    = var.app_password
}

# Cloud Tasks module
module "tasks" {
  source     = "../../modules/tasks"
  project_id = var.project_id
  region     = var.region
  queue_name = var.cloud_tasks_queue_name
}

# Cloud Run service that depends on the above resources
module "cloud_run_v2" {
  source  = "GoogleCloudPlatform/cloud-run/google//modules/v2"
  version = "~> 0.21"

  service_name           = var.service_name
  project_id             = var.project_id
  location               = var.region
  create_service_account = false
  service_account        = var.service_account_email
  execution_environment  = "EXECUTION_ENVIRONMENT_GEN2"

  template_scaling = {
    min_instance_count = 0
    max_instance_count = 10
  }

  ingress = "INGRESS_TRAFFIC_ALL"  # Allows unauthenticated access
  members = ["allUsers"]  # This makes it publicly accessible

  containers = [
    {
      container_image = var.image_url

      resources = {
        limits = { memory = "1Gi" }
      }

      volume_mounts = [
        {
          name       = "cloudsql"
          mount_path = "/cloudsql"
        }
      ]

      env_vars = {
        GOOGLE_CLOUD_PROJECT     = var.project_id
        REGION                   = var.region
        TELLME_ENV              = var.tellme_env
        DEBUG                   = "0"
        SETTINGS_NAME           = var.settings_name
        SQL_INSTANCE_NAME       = var.sql_instance_name
        DATABASE_NAME           = var.database_name
        GS_BUCKET_NAME          = google_storage_bucket.media_bucket.name
        CLOUD_TASKS_QUEUE_NAME  = module.tasks.queue_name
        CALL_PROCESSING_BUCKET  = var.call_processing_bucket
        FRONTEND_PATH           = var.frontend_path
        CALL_PROCESSING_ENDPOINT = "None"
      }
    }
  ]

  volumes = [
    {
      name = "cloudsql"
      cloud_sql_instance = {
        instances = [module.cloudsql.instance_connection_name]
      }
    }
  ]
}