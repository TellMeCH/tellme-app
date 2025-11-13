output "call_processing_queue_name" {
  value       = google_cloud_tasks_queue.call_processing_queue.name
  description = "Name of the call processing Cloud Tasks queue"
}

output "call_processing_queue_id" {
  value       = google_cloud_tasks_queue.call_processing_queue.id
  description = "ID of the call processing Cloud Tasks queue"
}

output "summarization_queue_name" {
  value       = google_cloud_tasks_queue.summarization_queue.name
  description = "Name of the summarization Cloud Tasks queue"
}

output "summarization_queue_id" {
  value       = google_cloud_tasks_queue.summarization_queue.id
  description = "ID of the summarization Cloud Tasks queue"
}