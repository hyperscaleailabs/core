"""Command-line interface for hsai."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .cluster import (
    ClusterError,
    doctor_cluster,
    format_json,
    format_plan,
    inspect,
    plan_cluster,
    provision_cluster,
    status_cluster,
)
from .config import Cluster, ConfigError, Inventory, Node, Target, default_config_path
from .remote import SshTransport


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hsai")
    parser.add_argument("--config", type=Path, default=default_config_path())
    groups = parser.add_subparsers(dest="group", required=True)

    target = groups.add_parser("target")
    target_commands = target.add_subparsers(dest="command", required=True)
    target_add = target_commands.add_parser("add")
    target_add.add_argument("name")
    target_add.add_argument("--ssh-host", required=True)
    target_add.add_argument("--ssh-user")
    target_add.add_argument("--ssh-port", type=int, default=22)
    target_commands.add_parser("list")
    target_inspect = target_commands.add_parser("inspect")
    target_inspect.add_argument("name")

    cluster = groups.add_parser("cluster")
    cluster_commands = cluster.add_subparsers(dest="command", required=True)
    cluster_create = cluster_commands.add_parser("create")
    cluster_create.add_argument("name")
    cluster_create.add_argument("--server", required=True)
    cluster_create.add_argument("--k3s-version", default="v1.33.3+k3s1")
    node = cluster_commands.add_parser("node-add")
    node.add_argument("cluster")
    node.add_argument("target")
    node.add_argument("--role", choices=["agent"], default="agent")
    for name in ("plan", "provision", "status", "doctor"):
        operation = cluster_commands.add_parser(name)
        operation.add_argument("cluster")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        inventory = Inventory.load(args.config)
        transport = SshTransport()
        if args.group == "target":
            return _target(args, inventory, transport)
        return _cluster(args, inventory, transport)
    except (ConfigError, ClusterError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def _target(args: argparse.Namespace, inventory: Inventory, transport: SshTransport) -> int:
    if args.command == "add":
        if args.name in inventory.targets:
            raise ConfigError(f"target {args.name!r} already exists")
        target = Target(
            name=args.name,
            ssh_host=args.ssh_host,
            ssh_user=args.ssh_user,
            ssh_port=args.ssh_port,
        )
        Target.from_dict(target.name, target.to_dict())
        inventory.targets[target.name] = target
        inventory.save(args.config)
        print(f"added target {target.name}")
    elif args.command == "list":
        for name in sorted(inventory.targets):
            print(name)
    else:
        print(format_json(inspect(inventory.targets[args.name], transport).__dict__))
    return 0


def _cluster(
    args: argparse.Namespace, inventory: Inventory, transport: SshTransport
) -> int:
    if args.command == "create":
        if args.name in inventory.clusters:
            raise ConfigError(f"cluster {args.name!r} already exists")
        if args.server not in inventory.targets:
            raise ConfigError(f"unknown target {args.server!r}")
        cluster = Cluster(
            name=args.name,
            nodes=(Node(target=args.server, role="server"),),
            k3s_version=args.k3s_version,
        )
        Cluster.from_dict(cluster.name, cluster.to_dict())
        inventory.clusters[cluster.name] = cluster
        inventory.save(args.config)
        print(f"created cluster {cluster.name}")
        return 0
    cluster = inventory.clusters[args.cluster]
    if args.command == "node-add":
        if args.target not in inventory.targets:
            raise ConfigError(f"unknown target {args.target!r}")
        updated = Cluster(
            name=cluster.name,
            nodes=(*cluster.nodes, Node(target=args.target, role=args.role)),
            k3s_version=cluster.k3s_version,
        )
        Cluster.from_dict(updated.name, updated.to_dict())
        inventory.clusters[cluster.name] = updated
        inventory.save(args.config)
        print(f"added {args.role} {args.target} to {cluster.name}")
    elif args.command == "plan":
        steps, _ = plan_cluster(inventory, cluster, transport)
        print(format_plan(steps))
        return 1 if any(step.action == "blocked" for step in steps) else 0
    elif args.command == "provision":
        print("\n".join(provision_cluster(inventory, cluster, transport)))
    elif args.command == "status":
        print(format_json(status_cluster(inventory, cluster, transport)))
    elif args.command == "doctor":
        healthy, findings = doctor_cluster(inventory, cluster, transport)
        print("\n".join(findings))
        return 0 if healthy else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
