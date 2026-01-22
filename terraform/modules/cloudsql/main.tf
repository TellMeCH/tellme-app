terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0"
    }
    postgresql = {
      source  = "cyrilgdn/postgresql"
      version = "~> 1.22"
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
    availability_type = var.availability_type

    ip_configuration {
      ssl_mode    = "TRUSTED_CLIENT_CERTIFICATE_REQUIRED"
      require_ssl = true
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

# PostgreSQL provider configuration for app user creation
# Note: This provider references resources that are created in the same module.
# The gcppostgres scheme handles authentication through Cloud SQL Proxy.
# During initial deployment, ensure that Cloud SQL instance is created before
# any postgresql resources are applied.
provider "postgresql" {
  scheme          = "gcppostgres"  # Uses Cloud SQL Proxy authentication
  host            = google_sql_database_instance.postgres_instance.connection_name
  port            = 5432
  username        = google_sql_user.admin_user.name
  password        = var.admin_password
  database        = google_sql_database.database.name
  sslmode         = "disable"  # Proxy handles SSL
  connect_timeout = 15
  superuser       = false      # Admin user is not a superuser
}

# Create application database user
resource "postgresql_role" "app_user" {
  name     = var.app_username
  login    = true
  password = var.app_password

  depends_on = [
    google_sql_database_instance.postgres_instance,
    google_sql_database.database,
    google_sql_user.admin_user
  ]
}

# Grant database-level privileges
resource "postgresql_grant" "app_user_database" {
  database    = google_sql_database.database.name
  role        = postgresql_role.app_user.name
  object_type = "database"
  privileges  = ["CONNECT", "CREATE", "TEMPORARY"]

  depends_on = [postgresql_role.app_user]
}

# Grant schema-level privileges
resource "postgresql_grant" "app_user_schema" {
  database    = google_sql_database.database.name
  role        = postgresql_role.app_user.name
  schema      = "public"
  object_type = "schema"
  privileges  = ["USAGE", "CREATE"]

  depends_on = [postgresql_role.app_user]
}

# Grant privileges on existing tables
resource "postgresql_grant" "app_user_tables" {
  database    = google_sql_database.database.name
  role        = postgresql_role.app_user.name
  schema      = "public"
  object_type = "table"
  privileges  = ["SELECT", "INSERT", "UPDATE", "DELETE", "REFERENCES", "TRIGGER"]

  depends_on = [postgresql_role.app_user]
}

# Grant privileges on existing sequences
resource "postgresql_grant" "app_user_sequences" {
  database    = google_sql_database.database.name
  role        = postgresql_role.app_user.name
  schema      = "public"
  object_type = "sequence"
  privileges  = ["USAGE", "SELECT", "UPDATE"]

  depends_on = [postgresql_role.app_user]
}

# Grant privileges on all future tables
resource "postgresql_default_privileges" "app_user_future_tables" {
  database    = google_sql_database.database.name
  role        = postgresql_role.app_user.name
  schema      = "public"
  owner       = google_sql_user.admin_user.name
  object_type = "table"
  privileges  = ["SELECT", "INSERT", "UPDATE", "DELETE", "REFERENCES", "TRIGGER"]

  depends_on = [postgresql_role.app_user]
}

# Grant privileges on all future sequences
resource "postgresql_default_privileges" "app_user_future_sequences" {
  database    = google_sql_database.database.name
  role        = postgresql_role.app_user.name
  schema      = "public"
  owner       = google_sql_user.admin_user.name
  object_type = "sequence"
  privileges  = ["USAGE", "SELECT", "UPDATE"]

  depends_on = [postgresql_role.app_user]
}

# Notification channels for database alerts
resource "google_monitoring_notification_channel" "db_alert_email" {
  for_each     = var.activate_alerts ? toset(var.alert_email_addresses) : []
  project      = var.project_id
  display_name = "DB Admin - ${each.value}"
  type         = "email"

  labels = {
    email_address = each.value
  }
}

# Alert policy for disk utilization
resource "google_monitoring_alert_policy" "disk_utilization" {
  count        = var.activate_alerts ? 1 : 0
  project      = var.project_id
  display_name = "Cloud SQL Disk Utilization - ${var.instance_name}"
  combiner     = "OR"

  conditions {
    display_name = "Disk utilization above 80%"

    condition_threshold {
      filter          = "resource.type = \"cloudsql_database\" AND resource.labels.database_id = \"${var.project_id}:${var.instance_name}\" AND metric.type = \"cloudsql.googleapis.com/database/disk/utilization\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.80  # 80% utilization

      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }

  notification_channels = [
    for channel in google_monitoring_notification_channel.db_alert_email : channel.id
  ]

  alert_strategy {
    auto_close = "604800s"  # 7 days
  }

  documentation {
    content   = "Cloud SQL instance ${var.instance_name} disk utilization has exceeded 80%. Consider increasing disk size or cleaning up old data."
    mime_type = "text/markdown"
  }
}