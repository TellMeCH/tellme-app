output "pool_name" {
  value = google_iam_workload_identity_pool.pool.name
}
output "provider_name" {
  value = google_iam_workload_identity_pool_provider.provider.name
}