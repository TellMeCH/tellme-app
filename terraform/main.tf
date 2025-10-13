terraform {
  required_version = ">= 1.0"

  cloud {
    organization = "tellme"

    workspaces {
      tags = ["tellme"]
    }
  }

  required_providers {
    google = {
      source = "hashicorp/google"
      version = "6.8.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.google_cloud_project
  region  = var.region
}

provider "google-beta" {
  project = var.google_cloud_project
  region  = var.region
}