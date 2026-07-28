#!/usr/bin/env python3
"""Pull a golden dataset slice into the canonical JSONL format.

Streams the source from Hugging Face (no full download), applies the golden's
field mapping, and writes goldens/cache/<golden>.<split>[.smoke].jsonl.
Audio columns are extracted to .wav files next to the JSONL.

Usage:
  python goldens/pull.py --golden coding-mbpp --split eval --limit 100
  python goldens/pull.py --golden voice-librispeech --split eval --limit 10 --smoke
"""

import argparse
import itertools
import json
import sys
from pathlib import Path

import yaml
from datasets import load_dataset

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_DIR = REPO_ROOT / "goldens" / "registry"
CACHE_DIR = REPO_ROOT / "goldens" / "cache"


def load_golden(name: str) -> dict:
    path = REGISTRY_DIR / f"{name}.yaml"
    if not path.exists():
        available = sorted(p.stem for p in REGISTRY_DIR.glob("*.yaml"))
        raise SystemExit(f"unknown golden '{name}'; available: {', '.join(available)}")
    return yaml.safe_load(path.read_text())


def normalize(row: dict, fields: dict, index: int, audio_dir: Path | None, modality: str) -> dict:
    record = {"modality": modality, "extra": {}}

    id_col = fields.get("id")
    record["id"] = str(row[id_col]) if id_col else str(index)

    if "audio" in fields:
        import io

        import soundfile as sf

        # audio column is cast to decode=False upstream: {"bytes": ..., "path": ...}
        audio = row[fields["audio"]]
        data, samplerate = sf.read(io.BytesIO(audio["bytes"]))
        audio_dir.mkdir(parents=True, exist_ok=True)
        wav_path = audio_dir / f"{record['id']}.wav"
        sf.write(wav_path, data, samplerate)
        record["input"] = str(wav_path)
    elif "input_template" in fields:
        record["input"] = fields["input_template"].format(**row)
    else:
        record["input"] = row[fields["input"]]

    ref_col = fields.get("reference")
    record["reference"] = row[ref_col] if ref_col else None

    for col in fields.get("extra", []):
        record["extra"][col] = row.get(col)
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--golden", required=True, help="golden name from goldens/registry/")
    parser.add_argument("--split", choices=["train", "eval"], default="eval")
    parser.add_argument("--limit", type=int, default=100, help="max records to pull")
    parser.add_argument("--smoke", action="store_true", help="use the golden's smoke_source")
    parser.add_argument("--out", default=None, help="output JSONL path (default: goldens/cache/)")
    args = parser.parse_args()

    golden = load_golden(args.golden)
    source_key = "smoke_source" if args.smoke else "source"
    if source_key not in golden:
        raise SystemExit(f"golden '{args.golden}' has no {source_key}")
    source = golden[source_key]
    hf_split = source["splits"][args.split]

    suffix = ".smoke" if args.smoke else ""
    out_path = Path(args.out) if args.out else CACHE_DIR / f"{args.golden}.{args.split}{suffix}.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    audio_dir = out_path.parent / f"{args.golden}.{args.split}{suffix}.audio"

    print(f"streaming {source['hf_id']} ({source.get('config', 'default')}/{hf_split})")
    stream = load_dataset(
        source["hf_id"],
        source.get("config"),
        split=hf_split,
        streaming=True,
    )

    if "audio" in golden["fields"]:
        from datasets import Audio

        # keep raw bytes; we decode with soundfile, avoiding the torch stack
        stream = stream.cast_column(golden["fields"]["audio"], Audio(decode=False))

    row_filter = source.get("row_filter", {}).get(args.split)
    if row_filter:
        stream = stream.filter(lambda r: r[row_filter["column"]] == row_filter["equals"])

    count = 0
    with out_path.open("w") as f:
        for index, row in enumerate(itertools.islice(stream, args.limit)):
            record = normalize(row, golden["fields"], index, audio_dir, golden["modality"])
            f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
            count += 1

    if count == 0:
        print("error: 0 records pulled (check split names and row_filter)", file=sys.stderr)
        sys.exit(1)
    print(f"wrote {count} records to {out_path}")


if __name__ == "__main__":
    main()
