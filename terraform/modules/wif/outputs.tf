output "pool_name" {
  # Full resource name, e.g.
  # projects/1234567890/locations/global/workloadIdentityPools/github-aeol-pool
  value = google_iam_workload_identity_pool.pool.name
}