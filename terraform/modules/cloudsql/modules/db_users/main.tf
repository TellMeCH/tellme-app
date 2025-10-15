terraform {
  required_providers {
    postgresql = {
      source  = "cyrilgdn/postgresql"
      version = "~> 1.0"
    }
  }
}

# THIS is the key: the provider is configured INSIDE the submodule
# It uses the connection_name passed from the parent
provider "postgresql" {
  scheme          = "gcppostgres"  # Uses Cloud SQL Proxy authentication
  host            = var.instance_connection_name  # project:region:instance format
  port            = 5432
  username        = var.admin_username
  password        = var.admin_password
  database        = var.database_name
  sslmode         = "disable"  # Proxy handles SSL
  connect_timeout = 15
}

# Create application database user
resource "postgresql_role" "app_user" {
  name     = var.app_username
  login    = true
  password = var.app_password
}

# Grant database-level privileges
resource "postgresql_grant" "app_user_database" {
  database    = var.database_name
  role        = postgresql_role.app_user.name
  object_type = "database"
  privileges  = ["ALL"]
}

# Grant schema-level privileges
resource "postgresql_grant" "app_user_schema" {
  database    = var.database_name
  role        = postgresql_role.app_user.name
  schema      = "public"
  object_type = "schema"
  privileges  = ["USAGE", "CREATE"]
}

# Grant privileges on all future tables
resource "postgresql_default_privileges" "app_user_tables" {
  database    = var.database_name
  role        = postgresql_role.app_user.name
  schema      = "public"
  owner       = var.admin_username
  object_type = "table"
  privileges  = ["ALL"]
}

# Grant privileges on all future sequences
resource "postgresql_default_privileges" "app_user_sequences" {
  database    = var.database_name
  role        = postgresql_role.app_user.name
  schema      = "public"
  owner       = var.admin_username
  object_type = "sequence"
  privileges  = ["ALL"]
}