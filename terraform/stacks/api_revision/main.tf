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
  allow_unauthenticated = true  # TODO: Check if exists
  cloudsql_instaces = vars.cloud_sql  # TODO: Check if exists

  containers = [
    {
      container_image = var.image_url
      resources = {
        limits = { memory = "1Gi" }
      }
      env_vars = {
        GOOGLE_CLOUD_PROJECT  = var.project_id
        REGION = var.region
        ...
      }
      env_secret_vars = {
        ...
        }
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