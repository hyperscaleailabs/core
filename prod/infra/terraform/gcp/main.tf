# GCP VM + k3s host for the Agent Simulation Control Plane (ASC-070, phase 2).
# Applied only after a human enables the project, billing, APIs, and provides credentials.

# --- Service account the VM runs as (reads secrets from Secret Manager) ---
resource "google_service_account" "vm" {
  account_id   = "${var.name_prefix}-k3s-host"
  display_name = "ASC k3s host"
}

resource "google_project_iam_member" "secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.vm.email}"
}

resource "google_project_iam_member" "log_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.vm.email}"
}

# --- Networking: static IP + firewall ---
resource "google_compute_address" "ip" {
  name = "${var.name_prefix}-ip"
}

resource "google_compute_firewall" "ssh" {
  name          = "${var.name_prefix}-allow-ssh"
  network       = "default"
  source_ranges = var.operator_cidrs
  target_tags   = ["${var.name_prefix}-k3s"]
  allow {
    protocol = "tcp"
    ports    = ["22"]
  }
}

resource "google_compute_firewall" "ingress" {
  name          = "${var.name_prefix}-allow-web"
  network       = "default"
  source_ranges = var.operator_cidrs
  target_tags   = ["${var.name_prefix}-k3s"]
  allow {
    protocol = "tcp"
    ports    = ["80", "443", "6443"] # ingress + kube-apiserver (restrict to operator CIDRs)
  }
}

# --- Data disk for stateful components ---
resource "google_compute_disk" "data" {
  name = "${var.name_prefix}-data"
  type = "pd-balanced"
  size = var.data_disk_gb
  zone = var.zone
}

# --- The VM ---
resource "google_compute_instance" "k3s" {
  name         = "${var.name_prefix}-k3s"
  machine_type = var.machine_type
  zone         = var.zone
  tags         = ["${var.name_prefix}-k3s"]
  labels       = var.labels

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2404-lts-amd64"
      size  = var.boot_disk_gb
      type  = "pd-balanced"
    }
  }

  attached_disk {
    source      = google_compute_disk.data.id
    device_name = "asc-data"
  }

  network_interface {
    network = "default"
    access_config {
      nat_ip = google_compute_address.ip.address
    }
  }

  metadata_startup_script = templatefile("${path.module}/startup.sh.tftpl", {
    repo_url = var.repo_url
    repo_ref = var.repo_ref
  })

  service_account {
    email  = google_service_account.vm.email
    scopes = ["cloud-platform"]
  }

  # k3s + data disk are provisioned by the startup script; allow it to finish before deploys.
  allow_stopping_for_update = true
}
