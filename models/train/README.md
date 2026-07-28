# Training

`finetune_lora.py` runs a LoRA SFT pass over a domain pack's
`typical_inputs.jsonl` (input -> reference pairs). The resulting adapter can
be served by the existing vLLM deployment with `--enable-lora`.

```bash
pip install -r train/requirements.txt
python train/finetune_lora.py --pack ecommerce
```

Runs on any single-GPU box; to use an SSH-provisioned cluster box, run it
directly on the host (or in a GPU pod) after syncing the repo there.

Roadmap:
- audio fine-tuning path for Ultravox / whisper distillation
- in-cluster training Jobs with checkpoint PVCs
