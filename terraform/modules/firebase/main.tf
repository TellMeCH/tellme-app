# Firebase Authentication Module
# Based on existing Firebase console configuration
# Note: APIs are enabled in infra/projects.tf

terraform {
  required_providers {
    google-beta = {
      source  = "hashicorp/google-beta"
      version = ">= 5.0"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = ">= 2.0"
    }
  }
}

# Main Identity Platform configuration
resource "google_identity_platform_config" "auth" {
  provider = google-beta
  project  = var.project_id

  # User account linking - Link accounts with same email
  sign_in {
    allow_duplicate_emails = false

    # Email/Password provider
    email {
      enabled           = true
      password_required = true
    }
  }

  # Authorized domains based on your current setup
  authorized_domains = var.authorized_domains
}

# Firebase Web App (required to get Web API key)
resource "google_firebase_web_app" "default" {
  provider     = google-beta
  project      = var.project_id
  display_name = "Web App - ${var.project_id}"

  depends_on = [google_identity_platform_config.auth]
}

# Create Google OAuth 2.0 Client for Firebase Authentication
resource "google_iap_client" "oauth_client" {
  provider     = google-beta
  display_name = "Firebase Auth Client - ${var.project_id}"
  brand        = google_iap_brand.project_brand.name
}

# Create OAuth brand (required for OAuth client)
resource "google_iap_brand" "project_brand" {
  provider          = google-beta
  support_email     = var.support_email
  application_title = var.app_name
  project           = var.project_id
}

# Azure AD App Registration for Microsoft Authentication
resource "azuread_application" "firebase_auth" {
  display_name     = "Firebase Auth - ${var.project_id}"
  sign_in_audience = "AzureADMultipleOrgs"

  web {
    homepage_url = var.homepage_url
    redirect_uris = var.redirect_uris

    implicit_grant {
      access_token_issuance_enabled = false
      id_token_issuance_enabled     = false
    }
  }

  required_resource_access {
    resource_app_id = "00000003-0000-0000-c000-000000000000" # Microsoft Graph

    resource_access {
      id   = "37f7f235-527c-4136-accd-4a02d197296e" # openid
      type = "Scope"
    }

    resource_access {
      id   = "7427e0e9-2fba-42fe-b0c0-848c9e6a8182" # offline_access
      type = "Scope"
    }
  }
}

# Create client secret for Azure AD app
resource "azuread_application_password" "firebase_auth" {
  application_id = azuread_application.firebase_auth.id
  display_name   = "Firebase Auth Secret"
}

# Google Sign-In Provider
resource "google_identity_platform_default_supported_idp_config" "google" {
  provider      = google-beta
  project       = var.project_id
  enabled       = true
  idp_id        = "google.com"
  client_id     = google_iap_client.oauth_client.client_id
  client_secret = google_iap_client.oauth_client.secret

  depends_on = [google_identity_platform_config.auth]
}

# Microsoft Sign-In Provider
resource "google_identity_platform_default_supported_idp_config" "microsoft" {
  provider      = google-beta
  project       = var.project_id
  enabled       = true
  idp_id        = "microsoft.com"
  client_id     = azuread_application.firebase_auth.id
  client_secret = azuread_application_password.firebase_auth.value

  depends_on = [google_identity_platform_config.auth]
}