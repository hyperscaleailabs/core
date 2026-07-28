# ADR-0007: Local k3d/k3s first, then GCP VM + k3s via Terraform

**Status:** Accepted · **Date:** 2026-07-24

## Context
The stakeholder wants the full stack running end-to-end on a **local k3s cluster** first, then a
**GCP VM provisioned with Terraform + k3s**. GCP access/keys require a human to enable them.

## Decision
- Phase 1: deploy to **local k3d/k3s** with one set of Kustomize/Helm manifests (`local`/`lite`
  overlays). Definition of done = golden Purchase Ambiguity workflow reproducible on the cluster.
- Phase 2: **Terraform** (`infra/terraform/gcp`) provisions a Compute Engine VM, installs
  single-node k3s via cloud-init, and rolls the **same manifests** (`gcp` overlay). Written and
  reviewed in phase 1; **applied only after** a human enables the GCP project, billing, APIs, and
  credentials.

## Consequences
- One manifest set across environments; environment differences isolated to overlays + secret
  sourcing.
- Phase-2 Terraform can be `validate`d in CI without credentials; `apply` is human-gated.
- Single-node k3s on a VM trades HA for simplicity/cost, appropriate for a pre-production tool.
