# Production environment configuration
environment = "prod"

# These values should match your current production environment
# Update based on your actual production configuration
service_name     = "tellme-service"
sql_instance_name = "tellme-app"
database_name    = "db"

media_bucket_suffix          = "static_files"
call_processing_bucket_suffix = "call_recordings"

cloud_tasks_queue_name = "call-processing"
artifact_repo         = "cloud-run-source-deploy"

# No monitoring function in production