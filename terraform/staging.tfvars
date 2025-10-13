# Staging environment configuration
environment = "staging"

# These values should match your current staging environment
# Update based on your actual staging configuration
service_name     = "tellme-service"
sql_instance_name = "tellme-app"
database_name    = "db"

media_bucket_suffix          = "static_files"
call_processing_bucket_suffix = "call_recordings"
monitoring_bucket_suffix      = "monitoring_data"

cloud_tasks_queue_name = "call-processing"
artifact_repo         = "cloud-run-source-deploy"
monitoring_function   = "langfuse-exporter"