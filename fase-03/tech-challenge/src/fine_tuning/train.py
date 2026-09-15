"""Fine-tuning QLoRA do modelo base com os dados médicos internos.

Roda em GPU (local CUDA ou Colab). Em Mac/CPU, use apenas --dry-run para
validar o pipeline de dados sem treinar.

Uso:
    python -m src.fine_tuning.train --dry-run          # valida dados/tokenização
    python -m src.fine_tuning.train --epochs 3         # treina (requer GPU)
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.config import ADAPTER_PATH, BASE_MODEL, DATA_PROCESSED


def load_jsonl(name: str) -> list[dict]:
    path = DATA_PROCESSED / name
    if not path.exists():
        raise SystemExit(f"Dataset não encontrado: {path}. Rode: python -m src.data_prep.build_dataset")
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def to_chat_text(example: dict, system_prompt: str, tokenizer) -> str:
    """Formato chat único — ponytail: usa o template do tokenizer, não inventa o nosso."""
    messages = [{"role": "system", "content": system_prompt}]
    user = example["instruction"] if not example.get("input") else f"{example['instruction']}\nContexto: {example['input']}"
    messages.append({"role": "user", "content": user})
    messages.append({"role": "assistant", "content": example["output"]})
    return tokenizer.apply_chat_template(messages, tokenize=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--dry-run", action="store_true", help="Só valida dados/tokenização, sem treinar")
    parser.add_argument("--no-quant", action="store_true",
                        help="LoRA full-precision (sem bitsandbytes) — usado em Apple Silicon/MPS")
    args = parser.parse_args()

    import torch
    from datasets import Dataset
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import LoraConfig
    from trl import SFTConfig, SFTTrainer

    meta = json.loads((DATA_PROCESSED / "meta.json").read_text(encoding="utf-8"))
    system_prompt = meta["system_prompt"]

    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    tokenizer.pad_token = tokenizer.pad_token or tokenizer.eos_token

    rows = load_jsonl("train.jsonl")
    texts = [to_chat_text(r, system_prompt, tokenizer) for r in rows]
    dataset = Dataset.from_dict({"text": texts})
    print(f"Exemplos de treino: {len(dataset)} | Exemplo formatado:\n{texts[0][:400]}...")

    if args.dry_run:
        print("Dry-run OK: dados, prompt e tokenização válidos. Para treinar, remova --dry-run (GPU necessária).")
        return

    use_quant = not args.no_quant and torch.cuda.is_available()
    device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")

    if use_quant:
        from transformers import BitsAndBytesConfig
        bnb = BitsAndBytesConfig(
            load_in_4bit=True, bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_use_double_quant=True,
        )
        model = AutoModelForCausalLM.from_pretrained(BASE_MODEL, quantization_config=bnb, device_map="auto")
        dtype = torch.bfloat16
        print(f"[train] QLoRA 4-bit (CUDA) — device={device}")
    else:
        model = AutoModelForCausalLM.from_pretrained(BASE_MODEL, torch_dtype=torch.float32)
        model = model.to(device)
        dtype = torch.float32
        print(f"[train] LoRA full-precision (sem quantização) — device={device}")

    lora = LoraConfig(
        r=16, lora_alpha=32, lora_dropout=0.05, bias="none", task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    )
    sft = SFTConfig(
        output_dir=str(ADAPTER_PATH),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=4,
        learning_rate=args.lr,
        lr_scheduler_type="cosine",
        logging_steps=10,
        save_strategy="epoch",
        bf16=dtype == torch.bfloat16,
        fp16=False,
        dataset_text_field="text",
        max_length=1024,
        report_to="none",
    )

    trainer = SFTTrainer(model=model, args=sft, train_dataset=dataset, peft_config=lora, processing_class=tokenizer)
    trainer.train()
    trainer.save_model(str(ADAPTER_PATH))
    tokenizer.save_pretrained(str(ADAPTER_PATH))
    print(f"Adapter LoRA salvo em: {ADAPTER_PATH}")


if __name__ == "__main__":
    main()
