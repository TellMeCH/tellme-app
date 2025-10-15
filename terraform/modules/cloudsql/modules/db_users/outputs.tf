output "app_username" {
  value       = postgresql_role.app_user.name
  description = "PostgreSQL app user (database-level privileges)"
}