module "secrets" {
  for_each = local.sa_envs
  source           = "../../modules/secrets"
  project_id       = module.project[each.key].project_id
  runtime_sa_email = google_service_account.github[each.key].email
  secret_ids       = ["django_settings", "superuser_passwords", "database_admin", "cicd_service_account_key"]
  tellme_env       = var.envs[each.key].environment
}