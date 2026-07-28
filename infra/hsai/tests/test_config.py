import json
import tempfile
import unittest
from pathlib import Path

from hsai.config import Cluster, ConfigError, Inventory


class InventoryTests(unittest.TestCase):
    def test_requires_exactly_one_server(self) -> None:
        with self.assertRaisesRegex(ConfigError, "exactly one server"):
            Cluster.from_dict(
                "bad",
                {"nodes": [{"target": "worker", "role": "agent"}]},
            )

    def test_rejects_unknown_cluster_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(
                json.dumps(
                    {
                        "targets": {},
                        "clusters": {
                            "bad": {
                                "nodes": [{"target": "missing", "role": "server"}]
                            }
                        },
                    }
                )
            )
            with self.assertRaisesRegex(ConfigError, "unknown target"):
                Inventory.load(path)

    def test_save_uses_private_permissions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            Inventory().save(path)
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
