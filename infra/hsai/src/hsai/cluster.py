"""Cluster inspection, planning, and provisioning."""

from __future__ import annotations

import json
import shlex
from dataclasses import dataclass
from typing import Iterable

from .config import Cluster, Inventory, Target
from .remote import Result, Transport


class ClusterError(RuntimeError):
    """Raised when a cluster operation cannot continue."""


@dataclass(frozen=True)
class HostFacts:
    reachable: bool
    os_id: str = ""
    tailscale_ip: str = ""
    sudo_noninteractive: bool = False
    k3s_version: str = ""
    k3s_active: bool = False
    nvidia_ready: bool = False
    free_kib: int = 0

    @classmethod
    def parse(cls, result: Result) -> "HostFacts":
        if result.returncode != 0:
            return cls(reachable=False)
        values: dict[str, str] = {}
        for line in result.stdout.splitlines():
            key, separator, value = line.partition("=")
            if separator:
                values[key] = value
        return cls(
            reachable=True,
            os_id=values.get("os_id", ""),
            tailscale_ip=values.get("tailscale_ip", ""),
            sudo_noninteractive=values.get("sudo_noninteractive") == "yes",
            k3s_version=values.get("k3s_version", ""),
            k3s_active=values.get("k3s_active") == "yes",
            nvidia_ready=values.get("nvidia_ready") == "yes",
            free_kib=int(values.get("free_kib", "0") or 0),
        )


INSPECT_COMMAND = r"""set -eu
. /etc/os-release
printf 'os_id=%s\n' "$ID"
printf 'tailscale_ip=%s\n' "$(tailscale ip -4 2>/dev/null || true)"
if sudo -n true 2>/dev/null; then echo sudo_noninteractive=yes; else echo sudo_noninteractive=no; fi
printf 'k3s_version=%s\n' "$(k3s --version 2>/dev/null | awk 'NR==1 {print $3}' || true)"
if systemctl is-active --quiet k3s 2>/dev/null || systemctl is-active --quiet k3s-agent 2>/dev/null; then echo k3s_active=yes; else echo k3s_active=no; fi
if nvidia-smi >/dev/null 2>&1; then echo nvidia_ready=yes; else echo nvidia_ready=no; fi
printf 'free_kib=%s\n' "$(df -Pk /var/lib | awk 'NR==2 {print $4}')"
"""


def inspect(target: Target, transport: Transport) -> HostFacts:
    return HostFacts.parse(transport.run(target, INSPECT_COMMAND))


@dataclass(frozen=True)
class PlanStep:
    target: str
    action: str
    reason: str


def plan_cluster(
    inventory: Inventory, cluster: Cluster, transport: Transport
) -> tuple[list[PlanStep], dict[str, HostFacts]]:
    steps: list[PlanStep] = []
    facts: dict[str, HostFacts] = {}
    server_target = inventory.targets[cluster.server.target]
    for node in cluster.nodes:
        target = inventory.targets[node.target]
        host = inspect(target, transport)
        facts[node.target] = host
        if not host.reachable:
            steps.append(PlanStep(node.target, "blocked", "SSH is not reachable"))
            continue
        if host.os_id != "debian":
            steps.append(PlanStep(node.target, "blocked", "target is not Debian"))
        if not host.tailscale_ip:
            steps.append(PlanStep(node.target, "blocked", "Tailscale IPv4 is unavailable"))
        if not host.sudo_noninteractive:
            steps.append(
                PlanStep(node.target, "blocked", "non-interactive sudo is unavailable")
            )
        if host.free_kib < 50 * 1024 * 1024:
            steps.append(PlanStep(node.target, "blocked", "less than 50 GiB is free"))
        if host.k3s_version != cluster.k3s_version:
            action = "install-server" if node.role == "server" else "install-agent"
            steps.append(
                PlanStep(
                    node.target,
                    action,
                    f"K3s {cluster.k3s_version} required; found {host.k3s_version or 'none'}",
                )
            )
        elif not host.k3s_active:
            steps.append(PlanStep(node.target, "start", "K3s service is inactive"))
        else:
            steps.append(PlanStep(node.target, "noop", "desired K3s version is active"))
    if not facts.get(server_target.name, HostFacts(False)).tailscale_ip:
        steps.append(PlanStep(server_target.name, "blocked", "server has no join address"))
    return steps, facts


def _server_install_command(cluster: Cluster, ip: str) -> str:
    version = shlex.quote(cluster.k3s_version)
    address = shlex.quote(ip)
    return (
        "curl -sfL https://get.k3s.io | "
        f"sudo env INSTALL_K3S_VERSION={version} "
        f"INSTALL_K3S_EXEC='server --node-ip {address} --advertise-address {address} "
        f"--tls-san {address} --flannel-iface tailscale0' sh -"
    )


def _agent_install_command(cluster: Cluster, server_ip: str, token: str) -> str:
    version = shlex.quote(cluster.k3s_version)
    url = shlex.quote(f"https://{server_ip}:6443")
    join_token = shlex.quote(token)
    return (
        "curl -sfL https://get.k3s.io | "
        f"sudo env INSTALL_K3S_VERSION={version} K3S_URL={url} "
        f"K3S_TOKEN={join_token} "
        "INSTALL_K3S_EXEC='agent --flannel-iface tailscale0' sh -"
    )


def provision_cluster(
    inventory: Inventory, cluster: Cluster, transport: Transport
) -> list[str]:
    steps, facts = plan_cluster(inventory, cluster, transport)
    blockers = [step for step in steps if step.action == "blocked"]
    if blockers:
        detail = "; ".join(f"{step.target}: {step.reason}" for step in blockers)
        raise ClusterError(f"provisioning blocked: {detail}")

    events: list[str] = []
    server = inventory.targets[cluster.server.target]
    server_facts = facts[cluster.server.target]
    server_step = next(step for step in steps if step.target == cluster.server.target)
    if server_step.action == "install-server":
        result = transport.run(
            server, _server_install_command(cluster, server_facts.tailscale_ip)
        )
        _require_success(result, server.name, "install server")
        events.append(f"{server.name}: installed K3s server")
    elif server_step.action == "start":
        _require_success(
            transport.run(server, "sudo systemctl start k3s"),
            server.name,
            "start server",
        )
        events.append(f"{server.name}: started K3s server")
    else:
        events.append(f"{server.name}: server unchanged")

    token_result = transport.run(server, "sudo cat /var/lib/rancher/k3s/server/node-token")
    _require_success(token_result, server.name, "read join token")
    token = token_result.stdout.strip()
    if not token:
        raise ClusterError("server returned an empty join token")

    for node in cluster.nodes:
        if node.role != "agent":
            continue
        target = inventory.targets[node.target]
        step = next(item for item in steps if item.target == node.target)
        if step.action == "install-agent":
            result = transport.run(
                target,
                _agent_install_command(cluster, server_facts.tailscale_ip, token),
            )
            _require_success(result, target.name, "install agent")
            events.append(f"{target.name}: installed K3s agent")
        elif step.action == "start":
            _require_success(
                transport.run(target, "sudo systemctl start k3s-agent"),
                target.name,
                "start agent",
            )
            events.append(f"{target.name}: started K3s agent")
        else:
            events.append(f"{target.name}: agent unchanged")
    return events


def status_cluster(
    inventory: Inventory, cluster: Cluster, transport: Transport
) -> dict[str, object]:
    nodes: dict[str, object] = {}
    for node in cluster.nodes:
        facts = inspect(inventory.targets[node.target], transport)
        nodes[node.target] = {"role": node.role, **facts.__dict__}
    return {"cluster": cluster.name, "k3s_version": cluster.k3s_version, "nodes": nodes}


def doctor_cluster(
    inventory: Inventory, cluster: Cluster, transport: Transport
) -> tuple[bool, list[str]]:
    status = status_cluster(inventory, cluster, transport)
    findings: list[str] = []
    for name, raw in status["nodes"].items():
        node = dict(raw)
        if not node["reachable"]:
            findings.append(f"FAIL {name}: SSH unreachable")
        if node["os_id"] != "debian":
            findings.append(f"FAIL {name}: Debian required")
        if not node["tailscale_ip"]:
            findings.append(f"FAIL {name}: Tailscale IPv4 missing")
        if not node["sudo_noninteractive"]:
            findings.append(f"FAIL {name}: non-interactive sudo missing")
        if not node["k3s_active"]:
            findings.append(f"FAIL {name}: K3s inactive")
        if int(node["free_kib"]) < 50 * 1024 * 1024:
            findings.append(f"FAIL {name}: insufficient free storage")
    if not findings:
        findings.append("PASS cluster prerequisites and K3s services")
    return not any(item.startswith("FAIL") for item in findings), findings


def format_plan(steps: Iterable[PlanStep]) -> str:
    return "\n".join(
        f"{step.action.upper():14} {step.target}: {step.reason}" for step in steps
    )


def format_json(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True)


def _require_success(result: Result, target: str, action: str) -> None:
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown error"
        raise ClusterError(f"{target}: failed to {action}: {detail}")
