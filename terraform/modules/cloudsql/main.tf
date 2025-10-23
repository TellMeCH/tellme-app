terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
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
}

# Create application database user
resource "postgresql_role" "app_user" {
  count    = var.create_app_user
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
  count       = var.create_app_user
  database    = google_sql_database.database.name
  role        = postgresql_role.app_user[0].name
  object_type = "database"
  privileges  = ["CONNECT", "CREATE", "TEMPORARY"]

  depends_on = [postgresql_role.app_user]
}

# Grant schema-level privileges
resource "postgresql_grant" "app_user_schema" {
  count       = var.create_app_user
  database    = google_sql_database.database.name
  role        = postgresql_role.app_user[0].name
  schema      = "public"
  object_type = "schema"
  privileges  = ["USAGE", "CREATE"]

  depends_on = [postgresql_role.app_user]
}

# Grant privileges on existing tables
resource "postgresql_grant" "app_user_tables" {
  count       = var.create_app_user
  database    = google_sql_database.database.name
  role        = postgresql_role.app_user[0].name
  schema      = "public"
  object_type = "table"
  privileges  = ["SELECT", "INSERT", "UPDATE", "DELETE"]

  depends_on = [postgresql_role.app_user]
}

# Grant privileges on existing sequences
resource "postgresql_grant" "app_user_sequences" {
  count       = var.create_app_user
  database    = google_sql_database.database.name
  role        = postgresql_role.app_user[0].name
  schema      = "public"
  object_type = "sequence"
  privileges  = ["USAGE", "SELECT", "UPDATE"]

  depends_on = [postgresql_role.app_user]
}

# Grant privileges on all future tables
resource "postgresql_default_privileges" "app_user_future_tables" {
  count       = var.create_app_user
  database    = google_sql_database.database.name
  role        = postgresql_role.app_user[0].name
  schema      = "public"
  owner       = google_sql_user.admin_user.name
  object_type = "table"
  privileges  = ["SELECT", "INSERT", "UPDATE", "DELETE"]

  depends_on = [postgresql_role.app_user]
}

# Grant privileges on all future sequences
resource "postgresql_default_privileges" "app_user_future_sequences" {
  count       = var.create_app_user
  database    = google_sql_database.database.name
  role        = postgresql_role.app_user[0].name
  schema      = "public"
  owner       = google_sql_user.admin_user.name
  object_type = "sequence"
  privileges  = ["USAGE", "SELECT", "UPDATE"]

  depends_on = [postgresql_role.app_user]
}