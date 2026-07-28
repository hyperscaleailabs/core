# Goldens: pluggable golden datasets

A **golden** is a local configuration that points to an external dataset
(typically on Hugging Face) and describes how to normalize it into the repo's
canonical record format. Goldens are the SDLC anchor of this repo: every
training run and benchmark is defined against a golden, and a model change is
judged by how its golden scores move.

Contrast with `datasets/domain-packs/`: domain packs are small, hand-curated,
in-repo failure-mode demonstrations; goldens are pointers to real external
datasets at scale. Both feed the same benchmark runner.

## Registry

One YAML per golden in `registry/`, validated by `golden.schema.json`:

| Golden | Domain | Modality | Source |
|--------|--------|----------|--------|
| `coding-mbpp` | coding | text | [google-research-datasets/mbpp](https://huggingface.co/datasets/google-research-datasets/mbpp) (sanitized) |
| `ecommerce-ecinstruct` | e-commerce | text | [NingLab/ECInstruct](https://huggingface.co/datasets/NingLab/ECInstruct) |
| `voice-librispeech` | voice/ASR | audio-asr | [openslr/librispeech_asr](https://huggingface.co/datasets/openslr/librispeech_asr) (clean) |

Each golden defines logical `train` and `eval` splits so fine-tuning and
benchmarking never touch the same rows. Audio goldens also define a
`smoke_source` - a tiny stand-in dataset (e.g. the 73-row LibriSpeech dummy)
so CI and local K3s smoke tests never download gigabytes.

## Pulling

`pull.py` streams the source dataset (no full download), applies the golden's
field mapping, and writes normalized JSONL to `goldens/cache/` (gitignored):

```bash
pip install -r goldens/requirements.txt

# first 100 eval items of the coding golden
python goldens/pull.py --golden coding-mbpp --split eval --limit 100

# first 100 training items of the e-commerce golden
python goldens/pull.py --golden ecommerce-ecinstruct --split train --limit 100

# tiny audio smoke set (writes .wav files next to the JSONL)
python goldens/pull.py --golden voice-librispeech --split eval --limit 10 --smoke
```

## Canonical record format

```json
{"id": "...", "modality": "text", "input": "...", "reference": "...", "extra": {}}
```

- `input`: the prompt, or for audio goldens the path to the extracted `.wav`
- `reference`: ground truth (code solution, expected answer, transcript)
- `extra`: passthrough columns the benchmark needs (e.g. `test_list` for
  executing MBPP unit tests)

## Adding a golden

Copy an existing registry YAML, point it at the new dataset, map the fields,
and check licensing (the `license` field is required; keep only
redistribution-safe sources). No code changes needed - `pull.py`, the
benchmark runner, and training discover goldens by name.
