"""Carrega a LLM: adapter fine-tunado se existir, senão base; mock para testes offline.

Modos (variável de ambiente LLM_MODE):
  - auto   (padrão): adapter fine-tunado se presente, senão base
  - base   : força modelo base
  - mock   : LLM determinística para testes/demonstração offline (sem download)
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.config import ADAPTER_PATH, BASE_MODEL, DISCLAIMER


class MockLLM:
    """LLM de teste: ecoa contexto com regras fixas — determinística, sem GPU/rede."""

    def invoke(self, prompt: str) -> str:
        proto_cited = ", ".join(sorted(set(p for p in prompt.split() if p.startswith("PROT-")))) or "nenhum protocolo recuperado"
        if "VALIDAÇÃO MÉDICA OBRIGATÓRIA" in prompt:
            return (
                "Sugestão de conduta conforme protocolos institucionais. "
                "Esta sugestão exige validação por médico responsável antes de qualquer prescrição. "
                f"Fontes: {proto_cited}." + DISCLAIMER
            )
        return (
            "Resposta de apoio à decisão baseada nos protocolos institucionais recuperados. "
            f"Fontes: {proto_cited}." + DISCLAIMER
        )


def load_llm():
    mode = os.getenv("LLM_MODE", "auto")
    if mode == "mock":
        print("[llm] modo mock (testes/offline)")
        return MockLLM()

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from langchain_huggingface import HuggingFacePipeline
    from transformers import pipeline

    device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
    use_adapter = mode == "auto" and ADAPTER_PATH.exists()
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    model = AutoModelForCausalLM.from_pretrained(BASE_MODEL, torch_dtype=torch.float32).to(device)
    if use_adapter:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, str(ADAPTER_PATH))
        print(f"[llm] modelo base + adapter fine-tunado ({ADAPTER_PATH})")
    else:
        print(f"[llm] modelo base ({BASE_MODEL})")

    pipe = pipeline(
        "text-generation", model=model, tokenizer=tokenizer, device=device,
        max_new_tokens=384, do_sample=False, return_full_text=False,
    )
    return HuggingFacePipeline(pipeline=pipe)
