terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

resource "google_sql_database_instance" "postgres_instance" {
  project          = var.project_id
  name             = var.instance_name
  database_version = "POSTGRES_17"
  region           = var.region

  settings {
    tier              = var.tier
    edition           = "ENTERPRISE"
    availability_type = "ZONAL"

    ip_configuration {
      ssl_mode = "TRUSTED_CLIENT_CERTIFICATE_REQUIRED"
    }

    password_validation_policy {
      enable_password_policy     = true
      complexity                 = "COMPLEXITY_DEFAULT"
    }
  }

  deletion_protection = var.deletion_protection
}

resource "google_sql_database" "database" {
  project  = var.project_id
  name     = var.database_name
  instance = google_sql_database_instance.postgres_instance.name
}

resource "google_sql_user" "admin_user" {
  project  = var.project_id
  name     = var.admin_username
  instance = google_sql_database_instance.postgres_instance.name
  password = var.admin_password
}

# Call nested module for database-level users
# This solves the provider dependency chicken-and-egg problem
module "db_users" {
  count  = var.create_app_user ? 1 : 0
  source = "./modules/db_users"

  # Pass COMPUTED values (not network resources)
  instance_connection_name = google_sql_database_instance.postgres_instance.connection_name
  database_name            = google_sql_database.database.name
  admin_username           = google_sql_user.admin_user.name
  admin_password           = var.admin_password

  # App user credentials
  app_username = var.app_username
  app_password = var.app_password

  # Explicit dependency ensures proper ordering
  depends_on = [
    google_sql_database_instance.postgres_instance,
    google_sql_database.database,
    google_sql_user.admin_user
  ]
}