variable "project_id" {
  type        = string
  description = "GCP project ID (billing enabled, compute.googleapis.com enabled)."
}

variable "region" {
  type    = string
  default = "us-central1"
}

variable "zone" {
  type    = string
  default = "us-central1-a"
}

variable "machine_type" {
  type        = string
  default     = "e2-standard-8" # 8 vCPU / 32 GB - Druid+Flink+Superset+Kafka are the heavy tenants
  description = "Compute Engine machine type for the single-node k3s host."
}

variable "boot_disk_gb" {
  type    = number
  default = 40
}

variable "data_disk_gb" {
  type        = number
  default     = 100
  description = "Persistent disk for Druid/Kafka/Postgres state (mounted at /var/lib/rancher)."
}

variable "operator_cidrs" {
  type        = list(string)
  description = "CIDRs allowed to reach SSH and the ingress (e.g. your office/home IP /32)."
  default     = []
}

variable "repo_url" {
  type        = string
  default     = "https://github.com/hyperscaleailabs/ai-multi-agent-simulation-eval-observability.git"
  description = "Repo the VM clones to run deploy/scripts on boot."
}

variable "repo_ref" {
  type    = string
  default = "main"
}

variable "name_prefix" {
  type    = string
  default = "asc"
}

variable "labels" {
  type    = map(string)
  default = { app = "agent-simulation-control-plane", managed-by = "terraform" }
}
