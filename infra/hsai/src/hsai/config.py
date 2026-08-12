"""External target and cluster inventory."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class ConfigError(ValueError):
    """Raised when inventory is invalid."""


def default_config_path() -> Path:
    override = os.environ.get("HSAI_CONFIG")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".hsailabs-core" / "hsai" / "config.json"


@dataclass(frozen=True)
class Target:
    name: str
    ssh_host: str
    ssh_user: str | None = None
    ssh_port: int = 22

    @classmethod
    def from_dict(cls, name: str, value: dict[str, Any]) -> "Target":
        host = value.get("ssh_host")
        if not isinstance(host, str) or not host:
            raise ConfigError(f"target {name!r} requires ssh_host")
        port = value.get("ssh_port", 22)
        if not isinstance(port, int) or not 1 <= port <= 65535:
            raise ConfigError(f"target {name!r} has invalid ssh_port")
        user = value.get("ssh_user")
        if user is not None and (not isinstance(user, str) or not user):
            raise ConfigError(f"target {name!r} has invalid ssh_user")
        return cls(name=name, ssh_host=host, ssh_user=user, ssh_port=port)

    @property
    def destination(self) -> str:
        return f"{self.ssh_user}@{self.ssh_host}" if self.ssh_user else self.ssh_host

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "ssh_host": self.ssh_host,
            "ssh_port": self.ssh_port,
        }
        if self.ssh_user:
            result["ssh_user"] = self.ssh_user
        return result


@dataclass(frozen=True)
class Node:
    target: str
    role: str

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "Node":
        target = value.get("target")
        role = value.get("role")
        if not isinstance(target, str) or not target:
            raise ConfigError("cluster node requires target")
        if role not in {"server", "agent"}:
            raise ConfigError(f"node {target!r} has invalid role {role!r}")
        return cls(target=target, role=role)

    def to_dict(self) -> dict[str, str]:
        return {"target": self.target, "role": self.role}


@dataclass(frozen=True)
class Cluster:
    name: str
    nodes: tuple[Node, ...] = field(default_factory=tuple)
    k3s_version: str = "v1.33.3+k3s1"

    @classmethod
    def from_dict(cls, name: str, value: dict[str, Any]) -> "Cluster":
        raw_nodes = value.get("nodes", [])
        if not isinstance(raw_nodes, list):
            raise ConfigError(f"cluster {name!r} nodes must be a list")
        nodes = tuple(Node.from_dict(node) for node in raw_nodes)
        servers = [node for node in nodes if node.role == "server"]
        if len(servers) != 1:
            raise ConfigError(f"cluster {name!r} requires exactly one server")
        targets = [node.target for node in nodes]
        if len(targets) != len(set(targets)):
            raise ConfigError(f"cluster {name!r} contains duplicate targets")
        version = value.get("k3s_version", "v1.33.3+k3s1")
        if not isinstance(version, str) or not version:
            raise ConfigError(f"cluster {name!r} requires k3s_version")
        return cls(name=name, nodes=nodes, k3s_version=version)

    @property
    def server(self) -> Node:
        return next(node for node in self.nodes if node.role == "server")

    def to_dict(self) -> dict[str, Any]:
        return {
            "k3s_version": self.k3s_version,
            "nodes": [node.to_dict() for node in self.nodes],
        }


@dataclass
class Inventory:
    targets: dict[str, Target] = field(default_factory=dict)
    clusters: dict[str, Cluster] = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path) -> "Inventory":
        if not path.exists():
            return cls()
        try:
            raw = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            raise ConfigError(f"cannot read inventory: {exc}") from exc
        if not isinstance(raw, dict):
            raise ConfigError("inventory root must be an object")
        targets = {
            name: Target.from_dict(name, value)
            for name, value in raw.get("targets", {}).items()
        }
        clusters = {
            name: Cluster.from_dict(name, value)
            for name, value in raw.get("clusters", {}).items()
        }
        for cluster in clusters.values():
            for node in cluster.nodes:
                if node.target not in targets:
                    raise ConfigError(
                        f"cluster {cluster.name!r} references unknown target {node.target!r}"
                    )
        return cls(targets=targets, clusters=clusters)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "version": 1,
            "targets": {
                name: target.to_dict() for name, target in sorted(self.targets.items())
            },
            "clusters": {
                name: cluster.to_dict() for name, cluster in sorted(self.clusters.items())
            },
        }
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(payload, indent=2) + "\n")
        temporary.chmod(0o600)
        temporary.replace(path)
        path.chmod(0o600)
