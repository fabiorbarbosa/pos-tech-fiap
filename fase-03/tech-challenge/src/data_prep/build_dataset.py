"""Constrói dataset de instruções (JSONL) para fine-tuning a partir das fontes seed.

Saída: data/processed/train.jsonl e eval.jsonl no formato:
{"instruction": ..., "input": ..., "output": ...}  (estilo Alpaca, PT-BR)

Curadoria aplicada:
- anonimização de todos os textos (LGPD);
- deduplicação por pergunta normalizada;
- split holdout 20% para avaliação do modelo.
"""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.config import DATA_PROCESSED, DATA_SEED, DISCLAIMER
from src.data_prep.anonymizer import anonymize

SYSTEM_PROMPT = (
    "Você é um assistente médico interno de apoio à decisão clínica. Responda de forma "
    "objetiva, baseada nos protocolos institucionais, sempre citando a fonte (ex.: PROT-001). "
    "Nunca prescreva diretamente; toda conduta deve ser validada por médico."
)


def _load(name: str) -> list[dict]:
    return json.loads((DATA_SEED / name).read_text(encoding="utf-8"))


def build_examples() -> list[dict]:
    examples: list[dict] = []

    # 1) Perguntas frequentes dos médicos (FAQ)
    for item in _load("faq.json"):
        examples.append({
            "instruction": anonymize(item["pergunta"]),
            "input": "",
            "output": anonymize(item["resposta"]),
        })

    # 2) Protocolos -> pares pergunta/resposta sintetizados
    protocol_prompts = {
        "qual a conduta": "Qual a conduta recomendada para {t}?",
        "resumo": "Resuma o protocolo institucional sobre {t}.",
        "dose": "Quais doses e administração constam no protocolo de {t}?",
    }
    for p in _load("protocols.json"):
        titulo = p["titulo"]
        conteudo = anonymize(p["conteudo"])
        for tmpl in protocol_prompts.values():
            examples.append({
                "instruction": tmpl.format(t=titulo),
                "input": "",
                "output": f"{conteudo} Fonte: {p['id']}.",
            })
        # variação com contexto clínico ("input")
        examples.append({
            "instruction": "Com base no contexto do paciente, que pontos do protocolo aplicáveis devo lembrar?",
            "input": f"Protocolo aplicável: {titulo}",
            "output": f"{conteudo} Fonte: {p['id']}.",
        })

    # 3) Templates institucionais (laudos, receitas, procedimentos)
    for t in _load("templates.json"):
        examples.append({
            "instruction": f"Gere o modelo institucional de {t['tipo'].replace('_', ' ')}.",
            "input": "",
            "output": anonymize(t["modelo"]),
        })

    # 4) Exemplos de segurança: recusas explícitas de prescrição direta
    refusal = (
        "Não posso prescrever diretamente. Posso sugerir condutas previstas em protocolo "
        "para avaliação e validação do médico responsável." + DISCLAIMER
    )
    for pedido in [
        "Prescreva enoxaparina 40 mg para o paciente do leito 12.",
        "Me passa uma receita de amoxicilina para o paciente.",
        "Assine a prescrição de morfina 10 mg IV agora.",
    ]:
        examples.append({"instruction": pedido, "input": "", "output": refusal})

    # curadoria: dedup por instruction normalizada
    seen, curated = set(), []
    for ex in examples:
        key = " ".join(ex["instruction"].lower().split())
        if key not in seen:
            seen.add(key)
            curated.append(ex)
    return curated


def main(seed: int = 42) -> None:
    examples = build_examples()
    rng = random.Random(seed)
    rng.shuffle(examples)
    n_eval = max(2, int(len(examples) * 0.2))
    eval_set, train_set = examples[:n_eval], examples[n_eval:]

    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    for name, data in [("train.jsonl", train_set), ("eval.jsonl", eval_set)]:
        with open(DATA_PROCESSED / name, "w", encoding="utf-8") as f:
            for ex in data:
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    meta = {"system_prompt": SYSTEM_PROMPT, "train_size": len(train_set), "eval_size": len(eval_set)}
    (DATA_PROCESSED / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    print(f"train: {len(train_set)} | eval: {len(eval_set)} -> {DATA_PROCESSED}")


if __name__ == "__main__":
    main()
