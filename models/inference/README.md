# Inference

Two serving paths:

1. **vLLM models** (Gemma, Ultravox): no custom image. The K3s manifests in
   `deploy/k3s/models/` run the upstream `vllm/vllm-openai` image with
   per-model arguments. Everything is configured in the manifest.

2. **faster-whisper**: not a vLLM-supported architecture (CTranslate2
   backend), so it gets its own small FastAPI container in
   `faster-whisper/`, exposing the same OpenAI-compatible
   `/v1/audio/transcriptions` API.

## Building the faster-whisper image

The registry is configurable (repo policy, CI-guarded: no
lab-specific registries hardcoded in this public repo). `registry.local` is
the neutral default used by the manifests; set `IMAGE_REGISTRY` to your own.

```bash
IMAGE_REGISTRY=${IMAGE_REGISTRY:-registry.local}
cd inference/faster-whisper
docker build -t "$IMAGE_REGISTRY/faster-whisper-server:latest" .
docker push "$IMAGE_REGISTRY/faster-whisper-server:latest"
```

For a local K3s without a registry, import the image directly (no push, the
`registry.local` name is then resolved from the node's local image store):

```bash
docker save registry.local/faster-whisper-server:latest \
  | sudo k3s ctr images import -
```

When using a real registry, point the manifests at it with a kustomize
override instead of editing them:

```yaml
# kustomization.yaml
images:
  - name: registry.local/faster-whisper-server
    newName: <your-registry>/faster-whisper-server
```
