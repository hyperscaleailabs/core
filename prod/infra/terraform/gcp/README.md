# GCP provisioning - VM + k3s (phase 2, human-gated)

Provisions a single Compute Engine VM, installs k3s via the startup script, and rolls the **same
manifests** as local (the `gcp` kustomize overlay). Written and CI-validated in phase 1; **applied
only after a human completes the checklist below.**

## Human-gating checklist (do these first - Terraform cannot)
- [ ] Create/choose a GCP project and **enable billing**.
- [ ] Enable APIs: `compute.googleapis.com`, `secretmanager.googleapis.com`, `iam.googleapis.com`.
- [ ] `gcloud auth application-default login` (or provide a service-account key via
      `GOOGLE_APPLICATION_CREDENTIALS`).
- [ ] Create the runtime secrets in **Secret Manager** (Postgres/MinIO/Superset/Grafana creds) - the
      values from `.env.example`. The VM's service account reads them (ASC-072).
- [ ] Put your egress IP in `operator_cidrs` (SSH, ingress, and kube-apiserver are restricted to it).

## Apply
```bash
cd infra/terraform/gcp
cp terraform.tfvars.example terraform.tfvars   # fill in project_id + operator_cidrs
terraform init
terraform plan
terraform apply
```

## After apply
```bash
terraform output ssh_command        # SSH in; startup script installs k3s + deploys the stack
terraform output kubeconfig_fetch   # fetch kubeconfig pointed at the external IP
terraform output urls               # operator-web URL
```

The startup script (`startup.sh.tftpl`) mounts the data disk at `/var/lib/rancher`, installs k3s +
helm, clones the repo at `repo_ref`, and runs `OVERLAY=gcp deploy/scripts/deploy-local.sh`. Fetch
the `.env` from Secret Manager before/at deploy time (do not bake secrets into the image or state).

## Teardown
```bash
terraform destroy
```

## Notes
- Single-node k3s trades HA for cost/simplicity - appropriate for a pre-production tool.
- Add DNS + TLS (cert-manager) and tighten firewall rules before any non-operator exposure.
- CI validates this module (`fmt`/`validate`/`tflint`) with **no apply** - see
  `.github/workflows/terraform-validate.yml`.
