#!/usr/bin/env python3
"""Benchmark a served model against a domain pack.

Measures latency/throughput on typical inputs and pass rates on
failure-mode probes.

Usage:
  python benchmark/run_benchmark.py \
      --endpoint http://<node>:30800/v1 \
      --model gemma-2-2b-it \
      --pack ecommerce
"""

import argparse
import json
import re
import statistics
import sys
import time
from pathlib import Path

import httpx
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
PACKS_DIR = REPO_ROOT / "datasets" / "domain-packs"


def load_pack(name: str) -> dict:
    pack_dir = PACKS_DIR / name
    meta = yaml.safe_load((pack_dir / "pack.yaml").read_text())
    for key, filename in meta["files"].items():
        lines = (pack_dir / filename).read_text().strip().splitlines()
        meta[key] = [json.loads(line) for line in lines if line.strip()]
    return meta


def chat(client: httpx.Client, endpoint: str, model: str, prompt: str) -> tuple[str, float]:
    start = time.monotonic()
    resp = client.post(
        f"{endpoint}/chat/completions",
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 512,
            "temperature": 0,
        },
        timeout=180,
    )
    latency = time.monotonic() - start
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"], latency


def run_check(check: dict, response: str) -> bool:
    kind = check["type"]
    lowered = response.lower()
    if kind == "must_contain":
        return any(v.lower() in lowered for v in check["values"])
    if kind == "must_not_contain":
        return all(v.lower() not in lowered for v in check["values"])
    if kind == "regex":
        return re.search(check["pattern"], response) is not None
    raise ValueError(f"unknown check type: {kind}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--endpoint", required=True, help="OpenAI-compatible base URL ending in /v1")
    parser.add_argument("--model", required=True, help="served model name")
    parser.add_argument("--pack", required=True, help="domain pack name under datasets/domain-packs/")
    parser.add_argument("--out", default=None, help="write full JSON report to this path")
    args = parser.parse_args()

    pack = load_pack(args.pack)
    client = httpx.Client()
    report = {"model": args.model, "pack": args.pack, "endpoint": args.endpoint}

    # -- latency / throughput on typical inputs --
    latencies = []
    print(f"== typical inputs ({len(pack['typical_inputs'])}) ==")
    for item in pack["typical_inputs"]:
        if item.get("modality", "text") != "text":
            continue
        response, latency = chat(client, args.endpoint, args.model, item["input"])
        latencies.append(latency)
        print(f"  {item['id']}: {latency:.2f}s, {len(response)} chars")

    if latencies:
        report["latency"] = {
            "count": len(latencies),
            "mean_s": round(statistics.mean(latencies), 3),
            "p50_s": round(statistics.median(latencies), 3),
            "max_s": round(max(latencies), 3),
            "throughput_rps": round(len(latencies) / sum(latencies), 3),
        }

    # -- failure-mode probes --
    print(f"== failure modes ({len(pack['failure_modes'])}) ==")
    results = []
    by_category: dict[str, list[bool]] = {}
    for probe in pack["failure_modes"]:
        if probe.get("modality", "text") != "text":
            continue
        response, _ = chat(client, args.endpoint, args.model, probe["input"])
        passed = run_check(probe["check"], response)
        by_category.setdefault(probe["category"], []).append(passed)
        results.append({"id": probe["id"], "category": probe["category"], "passed": passed, "response": response})
        print(f"  {probe['id']} [{probe['category']}]: {'PASS' if passed else 'FAIL'}")

    report["failure_modes"] = {
        "total": len(results),
        "passed": sum(r["passed"] for r in results),
        "by_category": {
            cat: f"{sum(vals)}/{len(vals)}" for cat, vals in sorted(by_category.items())
        },
        "results": results,
    }

    print("\n== summary ==")
    if "latency" in report:
        print(f"  latency p50 {report['latency']['p50_s']}s, mean {report['latency']['mean_s']}s")
    print(f"  failure-mode pass rate: {report['failure_modes']['passed']}/{report['failure_modes']['total']}")
    for cat, score in report["failure_modes"]["by_category"].items():
        print(f"    {cat}: {score}")

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(report, indent=2))
        print(f"\nreport written to {args.out}")

    return 0 if report["failure_modes"]["passed"] == report["failure_modes"]["total"] else 1


if __name__ == "__main__":
    sys.exit(main())
