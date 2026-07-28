import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from hsai.workload import WorkloadError, deploy_jax_smoke, deploy_model


class WorkloadTests(unittest.TestCase):
    @patch("hsai.workload.run_kubectl", return_value="ok\n")
    def test_gpu_deploy_scales_other_gpu_model_down(self, kubectl) -> None:
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

    def test_jax_deploy_rejects_latest_image(self) -> None:
        with self.assertRaisesRegex(WorkloadError, "immutable tag"):
            deploy_jax_smoke(Path("kubeconfig"), Path("manifest"), "jax:latest")
