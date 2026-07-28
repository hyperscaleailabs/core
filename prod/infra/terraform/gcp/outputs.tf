output "external_ip" {
  value       = google_compute_address.ip.address
  description = "Static external IP of the k3s host."
}

output "instance_name" {
  value = google_compute_instance.k3s.name
}

output "ssh_command" {
  value = "gcloud compute ssh ${google_compute_instance.k3s.name} --zone ${var.zone}"
}

output "kubeconfig_fetch" {
  value       = "gcloud compute scp ${google_compute_instance.k3s.name}:/etc/rancher/k3s/k3s.yaml ./kubeconfig --zone ${var.zone} && sed -i '' 's/127.0.0.1/${google_compute_address.ip.address}/' ./kubeconfig"
  description = "Fetch the kubeconfig and point it at the external IP."
}

output "urls" {
  value = {
    operator = "http://${google_compute_address.ip.address}/"
    note     = "Add DNS + TLS (cert-manager) before exposing publicly; restrict firewall to operator_cidrs."
  }
}
