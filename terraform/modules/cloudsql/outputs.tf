output "instance_name" {
  value       = google_sql_database_instance.postgres_instance.name
  description = "Name of the Cloud SQL instance"
}

output "instance_connection_name" {
  value       = google_sql_database_instance.postgres_instance.connection_name
  description = "Connection name for the Cloud SQL instance"
}

output "database_name" {
  value       = google_sql_database.database.name
  description = "Name of the database"
}

output "private_ip_address" {
  value       = google_sql_database_instance.postgres_instance.private_ip_address
  description = "Private IP address of the instance"
}

output "public_ip_address" {
  value       = google_sql_database_instance.postgres_instance.public_ip_address
  description = "Public IP address of the instance"
}

output "admin_username" {
  value       = google_sql_user.admin_user.name
  description = "Cloud SQL admin user (instance-level privileges)"
}

output "app_username" {
  value       = var.create_app_user ? module.db_users[0].app_username : null
  description = "PostgreSQL app user (database-level privileges)"
}