#!/usr/bin/env bash
# Provision K3s on a remote Debian box over SSH and fetch a working kubeconfig.
#
# Usage:
#   ./deploy/scripts/provision-k3s-ssh.sh user@host [ssh-port]
#
# Idempotent: re-running upgrades K3s in place and re-fetches the kubeconfig.
# The kubeconfig is written to .kube/remote-config (relative to the repo root)
# with the server address rewritten to the SSH host.
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "usage: $0 user@host [ssh-port]" >&2
  exit 1
fi

TARGET="$1"
SSH_PORT="${2:-22}"
HOST="${TARGET#*@}"
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
KUBECONFIG_OUT="$REPO_ROOT/.kube/remote-config"

SSH=(ssh -p "$SSH_PORT" -o StrictHostKeyChecking=accept-new "$TARGET")

echo "==> Checking remote OS"
"${SSH[@]}" 'grep -qi debian /etc/os-release || { echo "warning: target does not look like Debian" >&2; }'

echo "==> Installing prerequisites (curl, open-iscsi is not needed for base K3s)"
"${SSH[@]}" 'sudo apt-get update -qq && sudo apt-get install -y -qq curl'

echo "==> Installing/upgrading K3s (server, single node)"
# --tls-san makes the API server cert valid for the public address we SSH to,
# so the fetched kubeconfig works from this machine directly.
"${SSH[@]}" "curl -sfL https://get.k3s.io | sudo INSTALL_K3S_EXEC='server --tls-san $HOST --write-kubeconfig-mode 644' sh -"

echo "==> Waiting for node to be Ready"
"${SSH[@]}" 'until sudo k3s kubectl wait --for=condition=Ready node --all --timeout=10s >/dev/null 2>&1; do sleep 2; done; sudo k3s kubectl get nodes'

echo "==> Fetching kubeconfig to $KUBECONFIG_OUT"
mkdir -p "$(dirname "$KUBECONFIG_OUT")"
"${SSH[@]}" 'sudo cat /etc/rancher/k3s/k3s.yaml' \
  | sed "s/127.0.0.1/$HOST/" > "$KUBECONFIG_OUT"
chmod 600 "$KUBECONFIG_OUT"

echo "==> Verifying access from local machine"
kubectl --kubeconfig "$KUBECONFIG_OUT" get nodes

cat <<EOF

Done. Use the cluster with:

  export KUBECONFIG=$KUBECONFIG_OUT
  ./deploy/scripts/deploy.sh

Note: port 6443 (K3s API) must be reachable from this machine. If the box
only allows SSH, tunnel instead:
  ssh -p $SSH_PORT -L 6443:127.0.0.1:6443 $TARGET
and keep 127.0.0.1 in the kubeconfig.
EOF
