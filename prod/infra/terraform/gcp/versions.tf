terraform {
  required_version = ">= 1.6.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  # Configure a remote backend (GCS) before real use; local state is fine for the first bring-up.
  # backend "gcs" { bucket = "asc-tfstate"; prefix = "gcp/k3s" }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}
