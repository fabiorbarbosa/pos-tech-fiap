"""Avaliação do modelo base vs fine-tunado no conjunto holdout (eval.jsonl).

Métricas: ROUGE-L (implementação própria via LCS) e taxa de citação de fonte
(se a resposta cita 'PROT-XXX', verificação de explainability).

Uso:
    python -m src.fine_tuning.evaluate --max-new 256        # avalia base + adapter se existir
    python -m src.fine_tuning.evaluate --variant base       # só base
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.config import ADAPTER_PATH, BASE_MODEL, DATA_PROCESSED
from src.fine_tuning.train import load_jsonl, to_chat_text


def rouge_l(pred: str, ref: str) -> float:
    """ROUGE-L F1 via LCS em tokens — ponytail: sem dependência externa."""
    a, b = pred.lower().split(), ref.lower().split()
    if not a or not b:
        return 0.0
    prev = [0] * (len(b) + 1)
    for w in a:
        cur = [0]
        for j, wb in enumerate(b, 1):
            cur.append(prev[j - 1] + 1 if w == wb else max(prev[j], cur[-1]))
        prev = cur
    lcs = prev[-1]
    p, r = lcs / len(a), lcs / len(b)
    return 0.0 if (p + r) == 0 else 2 * p * r / (p + r)


def cites_source(text: str) -> bool:
    return "PROT-" in text or "Fonte:" in text


def generate(model, tokenizer, instruction: str, input_text: str, system_prompt: str, max_new: int) -> str:
    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": instruction if not input_text else f"{instruction}\nContexto: {input_text}"}]
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    ids = tokenizer(prompt, return_tensors="pt").to(model.device)
    out = model.generate(**ids, max_new_tokens=max_new, do_sample=False)
    return tokenizer.decode(out[0][ids["input_ids"].shape[1]:], skip_special_tokens=True).strip()


def evaluate_variant(name: str, model, tokenizer, eval_set, system_prompt, max_new: int) -> dict:
    scores, cited = [], 0
    for ex in eval_set:
        pred = generate(model, tokenizer, ex["instruction"], ex.get("input", ""), system_prompt, max_new)
        scores.append(rouge_l(pred, ex["output"]))
        cited += cites_source(pred)
    return {
        "variante": name,
        "n": len(eval_set),
        "rougeL_medio": round(sum(scores) / len(scores), 4),
        "taxa_citacao_fonte": round(cited / len(eval_set), 4),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-new", type=int, default=256)
    ap.add_argument("--variant", choices=["base", "finetuned", "ambos"], default="ambos")
    args = ap.parse_args()

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
    meta = json.loads((DATA_PROCESSED / "meta.json").read_text(encoding="utf-8"))
    eval_set = load_jsonl("eval.jsonl")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    results = []

    def load_model(adapter: Path | None):
        m = AutoModelForCausalLM.from_pretrained(BASE_MODEL, torch_dtype=torch.float32).to(device)
        if adapter:
            from peft import PeftModel
            m = PeftModel.from_pretrained(m, str(adapter))
        return m.eval()

    if args.variant in ("base", "ambos"):
        model = load_model(None)
        results.append(evaluate_variant("base", model, tokenizer, eval_set, meta["system_prompt"], args.max_new))
        del model
    if args.variant in ("finetuned", "ambos"):
        if ADAPTER_PATH.exists():
            model = load_model(ADAPTER_PATH)
            results.append(evaluate_variant("qlora_finetuned", model, tokenizer, eval_set, meta["system_prompt"], args.max_new))
        else:
            print(f"Adapter não encontrado em {ADAPTER_PATH} — rode o fine-tuning ou use --variant base.")

    out = {"metricas": results, "n_eval": len(eval_set)}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    (DATA_PROCESSED / "eval_results.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
