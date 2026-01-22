variable "project_id"       {
  type = string
}
variable "runtime_sa_email" {
  type = string
}
variable "secret_ids"       {
  type        = list(string)
  description = "List of secret names/ids. e.g., ['db-url', 'openai-api-token']"
}
variable "tellme_env" {
  type        = string
  description = "Environment (staging/prod)"
}