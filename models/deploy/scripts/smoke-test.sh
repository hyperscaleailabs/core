#!/usr/bin/env bash
# Smoke-test deployed model endpoints via their NodePorts.
#
# Usage:
#   ./deploy/scripts/smoke-test.sh [node-ip]
#   ./deploy/scripts/smoke-test.sh --model <deployment> [node-ip]
#
# Defaults to the first node's InternalIP from the current kubectl context.
set -euo pipefail

MODEL=""
if [[ "${1:-}" == "--model" ]]; then
  MODEL="${2:?--model requires a deployment name}"
  shift 2
fi
NODE_IP="${1:-$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')}"
echo "==> Testing against node $NODE_IP"
FAILED=0

check_vllm() {
  local name="$1" port="$2" model="$3"
  echo "--- $name (:$port) ---"
  if ! curl -sf --max-time 10 "http://$NODE_IP:$port/health" >/dev/null; then
    echo "FAIL: health check"
    FAILED=1
    return
  fi
  local reply
  reply=$(curl -sf --max-time 120 "http://$NODE_IP:$port/v1/chat/completions" \
    -H 'Content-Type: application/json' \
    -d "{\"model\":\"$model\",\"messages\":[{\"role\":\"user\",\"content\":\"Reply with the single word: pong\"}],\"max_tokens\":10}" \
    | python3 -c 'import json,sys; print(json.load(sys.stdin)["choices"][0]["message"]["content"])') || {
    echo "FAIL: chat completion"
    FAILED=1
    return
  }
  echo "OK: $reply"
}

check_whisper() {
  local port="$1"
  echo "--- faster-whisper (:$port) ---"
  if ! curl -sf --max-time 10 "http://$NODE_IP:$port/healthz" >/dev/null; then
    echo "FAIL: health check"
    FAILED=1
    return
  fi
  # 1s of silence as a wav, generated on the fly
  local wav
  wav=$(mktemp /tmp/smoke-XXXX.wav)
  python3 - "$wav" <<'PY'
import struct, sys, wave
with wave.open(sys.argv[1], "w") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
    w.writeframes(struct.pack("<h", 0) * 16000)
PY
  if curl -sf --max-time 60 "http://$NODE_IP:$port/v1/audio/transcriptions" \
      -F "file=@$wav" -F "model=faster-whisper-small" >/dev/null; then
    echo "OK: transcription endpoint responded"
  else
    echo "FAIL: transcription"
    FAILED=1
  fi
  rm -f "$wav"
}

case "$MODEL" in
  "") check_vllm "gemma-vllm" 30800 "gemma-2-2b-it"
      check_vllm "ultravox-vllm" 30801 "ultravox"
      check_whisper 30802 ;;
  gemma-vllm) check_vllm "gemma-vllm" 30800 "gemma-2-2b-it" ;;
  ultravox-vllm) check_vllm "ultravox-vllm" 30801 "ultravox" ;;
  faster-whisper) check_whisper 30802 ;;
  *) echo "unknown model deployment: $MODEL" >&2; exit 2 ;;
esac

exit "$FAILED"
