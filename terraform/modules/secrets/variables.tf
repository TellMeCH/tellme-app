variable "project_id"       { type = string }
variable "runtime_sa_email" { type = string }
variable "secret_ids"       { type = list(string) }  # e.g., ["db-url", "openai-api-token"]
