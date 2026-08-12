import tempfile
import unittest
import json
from pathlib import Path
from unittest.mock import patch

from hsai.workload import WorkloadError, deploy_jax_smoke, deploy_model


class WorkloadTests(unittest.TestCase):
    @patch("hsai.workload.run_kubectl")
    def test_gpu_deploy_scales_other_gpu_model_down(self, kubectl) -> None:
        kubectl.side_effect = [
            "namespace applied\n",
            json.dumps(
                {
                    "items": [
                        {"status": {"allocatable": {"nvidia.com/gpu": "1"}}}
                    ]
                }
            ),
            "secret exists\n",
            "other deployment exists\n",
            "scaled\n",
            "applied\n",
            "rolled out\n",
        ]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / "deploy/k3s/models/gemma-vllm.yaml"
            manifest.parent.mkdir(parents=True)
            manifest.write_text("kind: Deployment\n")
            deploy_model(Path("kubeconfig"), root, "gemma-vllm")
        calls = [call.args[1] for call in kubectl.call_args_list]
        self.assertIn(
            [
                "-n",
                "hyperswarm-models",
                "scale",
                "deployment/ultravox-vllm",
                "--replicas=0",
            ],
            calls,
        )

    @patch("hsai.workload.run_kubectl")
    def test_gpu_deploy_blocks_without_device_resource(self, kubectl) -> None:
        kubectl.side_effect = ["namespace applied\n", '{"items": []}']
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / "deploy/k3s/models/gemma-vllm.yaml"
            manifest.parent.mkdir(parents=True)
            manifest.write_text("kind: Deployment\n")
            with self.assertRaisesRegex(WorkloadError, "no allocatable"):
                deploy_model(Path("kubeconfig"), root, "gemma-vllm")

    def test_jax_deploy_rejects_latest_image(self) -> None:
        with self.assertRaisesRegex(WorkloadError, "immutable tag"):
            deploy_jax_smoke(Path("kubeconfig"), Path("manifest"), "jax:latest")
