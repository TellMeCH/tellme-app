module "secrets" {
  for_each = local.sa_envs
  source           = "../../modules/secrets"
  project_id       = module.project[each.key].project_id
  runtime_sa_email = google_service_account.sa[each.key].email
  secret_ids       = ["django_settings", "firebase_config", "superuser_passwords"]
}