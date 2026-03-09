terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 6.0"
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

    # Automated daily backups (Drata compliance)
    backup_configuration {
      enabled                        = var.enable_automated_backups
      start_time                     = "03:00"  # 3 AM UTC
      point_in_time_recovery_enabled = var.enable_automated_backups  # PITR requires backups to be enabled
      transaction_log_retention_days = var.enable_automated_backups ? 7 : null

      dynamic "backup_retention_settings" {
        for_each = var.enable_automated_backups ? [1] : []
        content {
          retained_backups = 30  # Keep 30 daily backups
          retention_unit   = "COUNT"
        }
      }
    }

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

# ==============================================================================
# Google Cloud Backup and DR Service (Enhanced Backups) — Production Only
# ==============================================================================
# ISO 27001-aligned immutable weekly backups, created only when tellme_env == "prod".
#
#   Vault       ← enforces 30-day minimum retention (WORM / immutability)
#   Plan        ← weekly schedule (Sunday 02:00–06:00 UTC), 30-day retention
#   Association ← links this Cloud SQL instance to the plan
#
# Required API: backupdr.googleapis.com (enabled via environments/infra/projects.tf)
# ==============================================================================

resource "google_backup_dr_backup_vault" "cloudsql_vault" {
  count    = var.tellme_env == "prod" ? 1 : 0
  project  = var.project_id
  location = var.region

  backup_vault_id = "${var.instance_name}-backup-vault"

  # Enforced minimum retention satisfies ISO 27001 immutability requirement.
  # Backups cannot be deleted before this duration expires (30 days = 2 592 000 s).
  backup_minimum_enforced_retention_duration = "2592000s"

  labels = {
    environment = var.tellme_env
    managed_by  = "terraform"
  }
}

resource "google_backup_dr_backup_plan" "cloudsql_plan" {
  count          = var.tellme_env == "prod" ? 1 : 0
  project        = var.project_id
  location       = var.region
  backup_plan_id = "${var.instance_name}-backup-plan"
  resource_type  = "sqladmin.googleapis.com/Instance"
  backup_vault   = google_backup_dr_backup_vault.cloudsql_vault[0].id

  backup_rules {
    rule_id               = "weekly-sunday"
    backup_retention_days = 30

    standard_schedule {
      recurrence_type = "WEEKLY"
      days_of_week    = ["SUNDAY"]
      time_zone       = "UTC"

      # Window: 02:00–08:00 UTC every Sunday (min 6 h required by Backup DR)
      backup_window {
        start_hour_of_day = 2
        end_hour_of_day   = 8
      }
    }
  }
}

resource "google_backup_dr_backup_plan_association" "cloudsql_association" {
  count                      = var.tellme_env == "prod" ? 1 : 0
  project                    = var.project_id
  location                   = var.region
  backup_plan_association_id = "${var.instance_name}-bpa"
  resource_type              = "sqladmin.googleapis.com/Instance"

  # Full GCP resource name for the Cloud SQL instance.
  resource = "//sqladmin.googleapis.com/projects/${var.project_id}/instances/${google_sql_database_instance.postgres_instance.name}"

  backup_plan = google_backup_dr_backup_plan.cloudsql_plan[0].name
}

# ==============================================================================
# Database Monitoring and Alerting (Drata Compliance)
# ==============================================================================
# When activate_alerts = true, creates email notification channels and 3 alert
# policies to monitor Cloud SQL database health and notify DB administrators:
#
# 1. Disk Utilization Alert (80% threshold)
#    - Monitors: cloudsql.googleapis.com/database/disk/utilization
#    - Triggers when storage exceeds 80% for 5 minutes
#    - Drata Test: "Database Free Storage Space Monitored"
#
# 2. Disk Read I/O Alert (10,000 ops/sec threshold)
#    - Monitors: cloudsql.googleapis.com/database/disk/read_ops_count
#    - Triggers when read operations exceed 10K/sec for 5 minutes
#    - Drata Test: "Database I/O Utilization Monitored"
#
# 3. CPU Utilization Alert (70% threshold)
#    - Monitors: cloudsql.googleapis.com/database/cpu/utilization
#    - Triggers when CPU usage exceeds 70% for 5 minutes
#    - Drata Test: "Database CPU Monitored"
#
# All alerts auto-close after 7 days and include actionable documentation.
# ==============================================================================

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

# Alert policy for disk read I/O
resource "google_monitoring_alert_policy" "disk_read_io" {
  count        = var.activate_alerts ? 1 : 0
  project      = var.project_id
  display_name = "Cloud SQL Disk Read I/O - ${var.instance_name}"
  combiner     = "OR"

  conditions {
    display_name = "Disk read I/O above 10000 ops/sec"

    condition_threshold {
      filter          = "resource.type = \"cloudsql_database\" AND resource.labels.database_id = \"${var.project_id}:${var.instance_name}\" AND metric.type = \"cloudsql.googleapis.com/database/disk/read_ops_count\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 10000  # 10000 operations per second

      aggregations {
        alignment_period     = "300s"
        per_series_aligner   = "ALIGN_RATE"
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
    content   = "Cloud SQL instance ${var.instance_name} disk read I/O has exceeded 10000 operations per second. This may indicate high database load or inefficient queries."
    mime_type = "text/markdown"
  }
}

# Alert policy for CPU utilization
resource "google_monitoring_alert_policy" "cpu_utilization" {
  count        = var.activate_alerts ? 1 : 0
  project      = var.project_id
  display_name = "Cloud SQL CPU Utilization - ${var.instance_name}"
  combiner     = "OR"

  conditions {
    display_name = "CPU utilization above 70%"

    condition_threshold {
      filter          = "resource.type = \"cloudsql_database\" AND resource.labels.database_id = \"${var.project_id}:${var.instance_name}\" AND metric.type = \"cloudsql.googleapis.com/database/cpu/utilization\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.70  # 70% CPU utilization

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
    content   = "Cloud SQL instance ${var.instance_name} CPU utilization has exceeded 70%. Consider scaling up the instance tier, optimizing queries, or adding read replicas."
    mime_type = "text/markdown"
  }
}