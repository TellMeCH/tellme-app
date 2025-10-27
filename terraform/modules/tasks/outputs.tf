output "queue_name" {
  value       = google_cloud_tasks_queue.queue.name
  description = "Name of the Cloud Tasks queue"
}

output "queue_id" {
  value       = google_cloud_tasks_queue.queue.id
  description = "ID of the Cloud Tasks queue"
}