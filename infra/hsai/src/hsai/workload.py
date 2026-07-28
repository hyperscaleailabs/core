"""Kubernetes workload deployment through a named hsai cluster."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Sequence


class WorkloadError(RuntimeError):
    """Raised when a Kubernetes workload operation fails."""


GPU_MODELS = {"gemma-vllm", "ultravox-vllm"}


def run_kubectl(kubeconfig: Path, args: Sequence[str], timeout: int = 900) -> str:
    process = subprocess.run(
        ["kubectl", "--kubeconfig", str(kubeconfig), *args],
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if process.returncode != 0:
        detail = process.stderr.strip() or process.stdout.strip() or "unknown error"
        raise WorkloadError(f"kubectl {' '.join(args)} failed: {detail}")
    return process.stdout


def deploy_model(
    kubeconfig: Path,
    models_root: Path,
    model: str,
) -> list[str]:
    manifest = models_root / "deploy" / "k3s" / "models" / f"{model}.yaml"
    if not manifest.is_file():
        raise WorkloadError(f"unknown model deployment {model!r}")
    events = [
        run_kubectl(kubeconfig, ["apply", "-k", str(models_root / "deploy/k3s/base")])
    ]
    if model in GPU_MODELS:
        _require_gpu(kubeconfig)
        _require_secret(kubeconfig, "hyperswarm-models", "hf-token")
        for other in sorted(GPU_MODELS - {model}):
            try:
                run_kubectl(
                    kubeconfig,
                    [
                        "-n",
                        "hyperswarm-models",
                        "get",
                        f"deployment/{other}",
                    ],
                )
            except WorkloadError:
                continue
            run_kubectl(
                kubeconfig,
                [
                    "-n",
                    "hyperswarm-models",
                    "scale",
                    f"deployment/{other}",
                    "--replicas=0",
                ],
            )
    events.append(run_kubectl(kubeconfig, ["apply", "-f", str(manifest)]))
    events.append(
        run_kubectl(
            kubeconfig,
            [
                "-n",
                "hyperswarm-models",
                "rollout",
                "status",
                f"deployment/{model}",
                "--timeout=15m",
            ],
        )
    )
    return events


def _require_gpu(kubeconfig: Path) -> None:
    output = run_kubectl(kubeconfig, ["get", "nodes", "-o", "json"])
    payload = json.loads(output)
    capacity = sum(
        int(node.get("status", {}).get("allocatable", {}).get("nvidia.com/gpu", 0))
        for node in payload.get("items", [])
    )
    if capacity < 1:
        raise WorkloadError(
            "cluster has no allocatable nvidia.com/gpu resource; "
            "repair the driver, container toolkit, and device plugin"
        )


def _require_secret(kubeconfig: Path, namespace: str, name: str) -> None:
    run_kubectl(kubeconfig, ["-n", namespace, "get", f"secret/{name}"])


def smoke_model(kubeconfig: Path, models_root: Path, model: str) -> str:
    script = models_root / "deploy" / "scripts" / "smoke-test.sh"
    process = subprocess.run(
        [str(script), "--model", model],
        check=False,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "KUBECONFIG": str(kubeconfig)},
    )
    if process.returncode != 0:
        raise WorkloadError(process.stderr.strip() or process.stdout.strip())
    return process.stdout


def deploy_jax_smoke(
    kubeconfig: Path,
    manifest: Path,
    image: str,
) -> str:
    if not image or image.endswith(":latest"):
        raise WorkloadError("JAX image must use an explicit immutable tag")
    rendered = manifest.read_text().replace("HSAI_JAX_IMAGE", image)
    if "HSAI_JAX_IMAGE" in rendered:
        raise WorkloadError("JAX image placeholder was not resolved")
    with tempfile.NamedTemporaryFile("w", suffix=".yaml") as temporary:
        temporary.write(rendered)
        temporary.flush()
        run_kubectl(kubeconfig, ["apply", "-f", temporary.name])
    return run_kubectl(
        kubeconfig,
        [
            "-n",
            "hyperswarm-models",
            "wait",
            "--for=condition=complete",
            "job/jax-train-validation-smoke",
            "--timeout=15m",
        ],
    )


def status_jax_smoke(kubeconfig: Path) -> str:
    output = run_kubectl(
        kubeconfig,
        [
            "-n",
            "hyperswarm-models",
            "get",
            "job/jax-train-validation-smoke",
            "-o",
            "json",
        ],
    )
    payload = json.loads(output)
    status = payload.get("status", {})
    return json.dumps(
        {
            "active": status.get("active", 0),
            "failed": status.get("failed", 0),
            "succeeded": status.get("succeeded", 0),
        },
        sort_keys=True,
    )


def smoke_jax(kubeconfig: Path) -> str:
    return run_kubectl(
        kubeconfig,
        [
            "-n",
            "hyperswarm-models",
            "logs",
            "job/jax-train-validation-smoke",
        ],
    )
