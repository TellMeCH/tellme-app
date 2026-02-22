# Get current project data
data "google_project" "current" {
  project_id = var.project_id
}

# Storage buckets
resource "google_storage_bucket" "media_bucket" {
  project  = var.project_id
  name     = "${var.project_id}_${var.media_bucket}"
  location = var.region
  uniform_bucket_level_access = false
  public_access_prevention    = "inherited"
  force_destroy               = false

  retention_policy {
    retention_period = 2678400
  }
  labels = {
    environment = var.tellme_env
  }
  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      num_newer_versions       = 3
      days_since_noncurrent_time = 31
    }
    action {
      type = "Delete"
    }
  }
}

resource "google_storage_bucket" "call_processing_bucket" {
  project  = var.project_id
  name     = "${var.project_id}_${var.call_processing_bucket}"
  location = var.region
  uniform_bucket_level_access = false
  public_access_prevention    = "inherited"
  force_destroy               = false

  retention_policy {
    retention_period = 2678400
  }
  labels = {
    environment = var.tellme_env
  }
  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      num_newer_versions       = 3
      days_since_noncurrent_time = 31
    }
    action {
      type = "Delete"
    }
  }
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
  source                   = "../../modules/cloudsql"
  project_id               = var.project_id
  region                   = var.region
  instance_name            = var.sql_instance_name
  database_name            = var.database_name
  admin_username           = var.admin_username
  admin_password           = var.admin_password
  app_username             = var.app_username
  app_password             = var.app_password
  availability_type        = var.availability_type
  activate_alerts          = var.activate_alerts
  alert_email_addresses    = var.alert_email_addresses
  enable_automated_backups = var.enable_automated_backups
}

# Cloud Tasks module
module "tasks" {
  source                       = "../../modules/tasks"
  project_id                   = var.project_id
  region                       = var.region
  call_processing_queue_name   = var.processing_queue_name
  summarization_queue_name     = var.summarization_queue_name
  tickets_queue_name           = var.tickets_queue_name
}

# Cloud Run service that depends on the above resources
module "cloud_run_v2" {
  source  = "GoogleCloudPlatform/cloud-run/google//modules/v2"
  version = "~> 0.21"

  service_name           = var.service_name
  project_id             = var.project_id
  location               = var.region
  create_service_account = false
  service_account        = google_service_account.app.email
  execution_environment  = "EXECUTION_ENVIRONMENT_GEN2"

  # Ensure IAM permissions and IAP service account are created before deploying Cloud Run
  depends_on = [
    google_secret_manager_secret_iam_member.runtime_django_settings,
    google_project_iam_member.runtime_cloudsql_client,
    google_project_iam_member.runtime_firebase_auth_admin,
    google_project_iam_member.runtime_cloudtasks_enqueuer,
    google_project_iam_member.runtime_cloudtasks_viewer,
    google_storage_bucket_iam_member.runtime_media_bucket,
    google_storage_bucket_iam_member.runtime_call_processing_bucket,
    google_project_service_identity.iap_sa
  ]

  template_scaling = {
    min_instance_count = var.min_instance_count
    max_instance_count = var.max_instance_count
  }

  max_instance_request_concurrency = var.max_concurrent_requests

  ingress = "INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER"
  members = [
   "serviceAccount:${google_service_account.app.email}",  # API Gateway can invoke
   "serviceAccount:service-${data.google_project.current.number}@gcp-sa-cloudtasks.iam.gserviceaccount.com",  # Cloud Tasks can invoke
   "serviceAccount:service-${data.google_project.current.number}@gcp-sa-iap.iam.gserviceaccount.com"  # IAP can invoke
  ]

  containers = [
    {
      container_image = var.image_url

      resources = {
        limits = {
          memory = var.instance_memory
          cpu    = var.instance_cpu
        }
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
        TELLME_ENV               = var.tellme_env
        DEBUG                    = "0"
        SETTINGS_NAME            = var.settings_name
        SQL_INSTANCE_NAME        = var.sql_instance_name
        DATABASE_NAME            = var.database_name
        GS_BUCKET_NAME           = google_storage_bucket.media_bucket.name
        PROCESSING_QUEUE_NAME    = module.tasks.call_processing_queue_name
        SUMMARIZATION_QUEUE_NAME = module.tasks.summarization_queue_name
        TICKETS_QUEUE_NAME       = module.tasks.tickets_queue_name
        CALL_PROCESSING_BUCKET   = var.call_processing_bucket
        FRONTEND_PATH            = var.frontend_path
        CALL_PROCESSING_ENDPOINT = "None"
        SUMMARIZATION_ENDPOINT   = "None"
        TICKETS_ENDPOINT         = "None"
        SERVICE_ACCOUNT_EMAIL    = google_service_account.app.email
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

locals {
  spec_rendered = templatefile("${path.module}/../../configs/spec.yaml", {
    cloud_run_url = module.cloud_run_v2.service_uri
  })
  api_config_id = "cfg-${substr(sha256(local.spec_rendered), 0, 8)}"
}

resource "google_api_gateway_api" "api" {
  provider = google-beta
  project  = var.project_id
  api_id   = "tellme-api"
}

resource "google_api_gateway_api_config" "cfg" {
  provider      = google-beta
  project       = var.project_id
  api           = google_api_gateway_api.api.api_id
  api_config_id = local.api_config_id

  openapi_documents {
    document {
      path     = "../../configs/spec.yaml"
      contents = base64encode(local.spec_rendered)
    }
  }

  gateway_config {
    backend_config {
      google_service_account = google_service_account.app.email
    }
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "google_api_gateway_gateway" "gateway" {
  provider   = google-beta
  project    = var.project_id
  region     = var.gateway_region
  gateway_id = "tellme-gateway"

  api_config = google_api_gateway_api_config.cfg.name
}

