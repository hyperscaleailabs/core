# Benchmark

`run_benchmark.py` drives any OpenAI-compatible endpoint (all our serving
paths) with a domain pack:

1. **Typical inputs**: sequential requests, reporting latency percentiles and
   throughput.
2. **Failure-mode probes**: each probe's `check` assertion is executed against
   the model response; results are aggregated per failure category.

Exit code is non-zero if any failure-mode probe fails, so it can gate CI.

```bash
pip install -r benchmark/requirements.txt
python benchmark/run_benchmark.py \
  --endpoint http://192.168.1.50:30800/v1 \
  --model gemma-2-2b-it \
  --pack ecommerce \
  --out benchmark/results/gemma-ecommerce.json
```

Audio packs (modality `audio-asr` / `audio-text`) are skipped by the text
driver for now; an audio driver is the next increment.
