#!/usr/bin/env python3
"""LoRA fine-tune of a chat model on canonical JSONL examples.

Data source is either a domain pack (--pack) or any canonical-format JSONL
(--data), e.g. a golden slice pulled by goldens/pull.py. Each row becomes one
(input -> reference) chat example. Defaults target Gemma 2 2B on a single GPU;
pass a tiny model for CPU smoke runs.

Usage:
  python train/finetune_lora.py --pack ecommerce
  python goldens/pull.py --golden ecommerce-ecinstruct --split train --limit 100
  python train/finetune_lora.py --data goldens/cache/ecommerce-ecinstruct.train.jsonl \
      --model HuggingFaceTB/SmolLM2-135M-Instruct --limit 32 --epochs 2
"""

import argparse
import json
from pathlib import Path

import torch
from datasets import Dataset
from peft import LoraConfig
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import SFTConfig, SFTTrainer

REPO_ROOT = Path(__file__).resolve().parent.parent
PACKS_DIR = REPO_ROOT / "datasets" / "domain-packs"


def load_examples(path: Path, limit: int | None) -> Dataset:
    rows = [json.loads(line) for line in path.read_text().strip().splitlines()]
    examples = [
        {
            "messages": [
                {"role": "user", "content": row["input"]},
                {"role": "assistant", "content": row["reference"]},
            ]
        }
        for row in rows
        if row.get("modality", "text") == "text" and row.get("reference")
    ]
    if limit:
        examples = examples[:limit]
    if not examples:
        raise SystemExit(f"no trainable text examples in {path}")
    return Dataset.from_list(examples)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--pack", help="domain pack name under datasets/domain-packs/")
    source.add_argument("--data", help="canonical-format JSONL path (e.g. a pulled golden slice)")
    parser.add_argument("--model", default="google/gemma-2-2b-it")
    parser.add_argument("--out", default=None)
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--limit", type=int, default=None, help="use only the first N examples")
    args = parser.parse_args()

    data_path = PACKS_DIR / args.pack / "typical_inputs.jsonl" if args.pack else Path(args.data)
    dataset_name = args.pack or data_path.stem
    out_dir = args.out or f"out/{args.model.split('/')[-1]}-{dataset_name}-lora"
    dataset = load_examples(data_path, args.limit)
    print(f"loaded {len(dataset)} examples from {data_path}")

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, device_map="auto")

    peft_config = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    )
    training_args = SFTConfig(
        output_dir=out_dir,
        num_train_epochs=args.epochs,
        learning_rate=args.lr,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        logging_steps=1,
        save_strategy="epoch",
        bf16=torch.cuda.is_available(),
    )
    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        processing_class=tokenizer,
        peft_config=peft_config,
    )
    trainer.train()
    trainer.save_model(out_dir)
    print(f"adapter saved to {out_dir}")
    print("serve it with vLLM: --enable-lora --lora-modules "
          f"{dataset_name}={out_dir}")


if __name__ == "__main__":
    main()
