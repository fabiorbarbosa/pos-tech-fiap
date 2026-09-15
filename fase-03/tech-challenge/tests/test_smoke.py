"""Smoke tests — roda offline com MockLLM, sem GPU/rede.

    python tests/test_smoke.py
"""
import os
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["LLM_MODE"] = "mock"

from src.data_prep.anonymizer import anonymize
from src.data_prep.build_dataset import build_examples
from src.assistant import guardrails
from src.assistant import rag
from src.assistant.graph import run
from src.assistant.llm import MockLLM
from src.assistant.tools import get_patient_exams, patient_context_text


def test_anonymizer():
    out = anonymize("O Dr. João Silva atendeu a Maria Souza, CPF 123.456.789-00, tel (11) 98765-4321")
    assert "123.456.789-00" not in out
    assert "João Silva" not in out
    assert "Maria Souza" not in out


def test_dataset_size_and_format():
    ex = build_examples()
    assert len(ex) >= 40, f"esperado >= 40 exemplos, veio {len(ex)}"
    for e in ex:
        assert {"instruction", "input", "output"} <= set(e)
    # sem dados pessoais
    joined = " ".join(e["instruction"] + e["output"] for e in ex)
    assert "@" not in joined.replace("[EMAIL]", "")


def test_guardrails():
    assert guardrails.check_input("Prescreva 40 mg de enoxaparina")["blocked"]
    assert guardrails.check_input("Paciente inconsciente e não respira")["blocked"]
    assert not guardrails.check_input("Qual a conduta na sepse?")["blocked"]
    assert guardrails.check_output("Iniciar ceftriaxona 1 g")["needs_human_validation"]


def test_tools():
    ctx = patient_context_text(1)
    assert "Paciente 1" in ctx and "PENDENTES" in ctx
    assert any(e["status"] == "pendente" for e in get_patient_exams(1, only_pending=True))


def test_rag_falls_back_when_vector_store_is_unavailable():
    with patch.dict(os.environ, {"LLM_MODE": "auto"}):
        with patch.object(rag, "_get_store", side_effect=RuntimeError("sem rede")):
            results = rag.search_protocols("Qual a conduta na sepse?")
    assert results and results[0]["fonte"].startswith("PROT-")


def test_rag_mock_mode_never_loads_vector_store():
    with patch.object(rag, "_get_store", side_effect=AssertionError("não deve acessar embeddings")):
        results = rag.search_protocols("Qual a conduta na sepse?")
    assert results and results[0]["fonte"].startswith("PROT-")


def test_graph_flow_with_mock():
    llm = MockLLM()
    # fluxo normal: responde com fonte
    r = run("Qual a conduta na sepse?", patient_id=1, llm=llm)
    assert "Fontes" in r, "resposta deve listar fontes (explainability)"
    # prescrição direta: bloqueado
    r2 = run("Prescreva 40 mg agora", patient_id=1, llm=llm)
    assert "Prescrição direta não é permitida" in r2 or "escalon" in r2.lower()


if __name__ == "__main__":
    for name, fn in [(k, v) for k, v in list(globals().items()) if k.startswith("test_")]:
        fn()
        print(f"PASS: {name}")
    print("\nTodos os smoke tests passaram.")
