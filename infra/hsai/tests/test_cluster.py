import unittest

from hsai.cluster import (
    ClusterError,
    _agent_install_command,
    _server_install_command,
    fetch_kubeconfig,
    plan_cluster,
    provision_cluster,
)
from hsai.config import Cluster, Inventory, Node, Target
from hsai.remote import Result


def facts(
    *,
    ip: str,
    version: str = "",
    active: bool = False,
    sudo: bool = True,
    nvidia: bool = False,
) -> str:
    return "\n".join(
        [
            "os_id=debian",
            f"tailscale_ip={ip}",
            f"sudo_noninteractive={'yes' if sudo else 'no'}",
            f"k3s_version={version}",
            f"k3s_active={'yes' if active else 'no'}",
            f"nvidia_ready={'yes' if nvidia else 'no'}",
            f"free_kib={200 * 1024 * 1024}",
        ]
    )


class MockTransport:
    def __init__(self, responses: dict[str, list[Result]]) -> None:
        self.responses = responses
        self.commands: list[tuple[str, str]] = []

    def run(self, target: Target, command: str) -> Result:
        self.commands.append((target.name, command))
        responses = self.responses.get(target.name, [])
        if responses:
            return responses.pop(0)
        return Result(0, "", "")


class ClusterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cluster = Cluster(
            "models",
            (
                Node("server", "server"),
                Node("worker-a", "agent"),
                Node("worker-b", "agent"),
            ),
        )
        self.inventory = Inventory(
            targets={
                name: Target(name, name)
                for name in ("server", "worker-a", "worker-b")
            },
            clusters={"models": self.cluster},
        )

    def test_plan_is_inspection_only(self) -> None:
        transport = MockTransport(
            {
                "server": [Result(0, facts(ip="100.64.0.1"), "")],
                "worker-a": [Result(0, facts(ip="100.64.0.2"), "")],
                "worker-b": [Result(0, facts(ip="100.64.0.3"), "")],
            }
        )
        steps, _ = plan_cluster(self.inventory, self.cluster, transport)
        self.assertEqual(
            [step.action for step in steps],
            ["install-server", "install-agent", "install-agent"],
        )
        self.assertTrue(all("curl" not in command for _, command in transport.commands))

    def test_plan_blocks_without_sudo(self) -> None:
        transport = MockTransport(
            {
                "server": [Result(0, facts(ip="100.64.0.1", sudo=False), "")],
                "worker-a": [Result(0, facts(ip="100.64.0.2"), "")],
                "worker-b": [Result(0, facts(ip="100.64.0.3"), "")],
            }
        )
        steps, _ = plan_cluster(self.inventory, self.cluster, transport)
        self.assertIn("blocked", [step.action for step in steps])

    def test_mock_provision_installs_server_then_agents(self) -> None:
        transport = MockTransport(
            {
                "server": [
                    Result(0, facts(ip="100.64.0.1"), ""),
                    Result(0, "", ""),
                    Result(0, "join-token\n", ""),
                ],
                "worker-a": [
                    Result(0, facts(ip="100.64.0.2"), ""),
                    Result(0, "", ""),
                ],
                "worker-b": [
                    Result(0, facts(ip="100.64.0.3"), ""),
                    Result(0, "", ""),
                ],
            }
        )
        events = provision_cluster(self.inventory, self.cluster, transport)
        self.assertEqual(len(events), 3)
        mutation_commands = [
            command for _, command in transport.commands if "get.k3s.io" in command
        ]
        self.assertEqual(len(mutation_commands), 3)
        self.assertIn("server --node-ip 100.64.0.1", mutation_commands[0])
        self.assertIn("K3S_URL=https://100.64.0.1:6443", mutation_commands[1])
        self.assertNotIn("join-token", repr(events))

    def test_provision_stops_on_preflight_blocker(self) -> None:
        transport = MockTransport(
            {
                "server": [Result(0, facts(ip="100.64.0.1", sudo=False), "")],
                "worker-a": [Result(0, facts(ip="100.64.0.2"), "")],
                "worker-b": [Result(0, facts(ip="100.64.0.3"), "")],
            }
        )
        with self.assertRaisesRegex(ClusterError, "non-interactive sudo"):
            provision_cluster(self.inventory, self.cluster, transport)
        self.assertTrue(all("get.k3s.io" not in cmd for _, cmd in transport.commands))

    def test_install_commands_pin_version_and_overlay_interface(self) -> None:
        server = _server_install_command(self.cluster, "100.64.0.1")
        agent = _agent_install_command(self.cluster, "100.64.0.1", "secret")
        self.assertIn("INSTALL_K3S_VERSION=", server)
        self.assertIn("--flannel-iface tailscale0", server)
        self.assertIn("--flannel-iface tailscale0", agent)

    def test_kubeconfig_uses_overlay_address_and_private_mode(self) -> None:
        import tempfile
        from pathlib import Path

        single = Cluster("models", (Node("server", "server"),))
        inventory = Inventory(
            targets={"server": Target("server", "server")},
            clusters={"models": single},
        )
        transport = MockTransport(
            {
                "server": [
                    Result(0, facts(ip="100.64.0.1"), ""),
                    Result(
                        0,
                        "clusters:\n- cluster:\n    server: https://127.0.0.1:6443\n",
                        "",
                    ),
                ]
            }
        )
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "models.yaml"
            fetch_kubeconfig(inventory, single, transport, output)
            self.assertIn("https://100.64.0.1:6443", output.read_text())
            self.assertEqual(output.stat().st_mode & 0o777, 0o600)
