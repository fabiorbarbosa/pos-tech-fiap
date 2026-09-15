"""Fluxo do assistente médico em LangGraph.

Pipeline:
  guardrail_entrada -> busca_contexto (paciente SQL + protocolos RAG)
    -> gera_resposta (LLM) -> validacao_saida (guardrail pós) -> auditoria

Cada nó é uma função pura sobre o estado; arestas condicionais fazem
short-circuit para bloqueio de entrada.
"""
import json
import sys
from pathlib import Path
from typing import TypedDict

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from langgraph.graph import END, START, StateGraph

from src.assistant import audit, guardrails, rag, tools


class AssistantState(TypedDict, total=False):
    pergunta: str
    patient_id: int | None
    blocked: bool
    block_message: str | None
    patient_context: str
    protocolos: list[dict]
    prompt: str
    resposta: str
    needs_human_validation: bool
    fontes: list[str]


_llm = None  # lazy: injetado via build_graph(llm=...)


def guardrail_entrada(state: AssistantState) -> AssistantState:
    r = guardrails.check_input(state["pergunta"])
    return {"blocked": r["blocked"], "block_message": r["message"]}


def busca_contexto(state: AssistantState) -> AssistantState:
    patient_id = state.get("patient_id")
    ctx = tools.patient_context_text(patient_id) if patient_id else ""
    protocolos = rag.search_protocols(state["pergunta"])
    return {"patient_context": ctx, "protocolos": protocolos}


def gera_resposta(state: AssistantState) -> AssistantState:
    proto_txt = "\n\n".join(
        f"[{p['fonte']}] {p['titulo']}\n{p['trecho']}" for p in state["protocolos"]
    )
    prompt = (
        "Você é um assistente médico de apoio à decisão. Responda de forma objetiva "
        "com base APENAS nos protocolos fornecidos e cite as fontes (ex.: PROT-001). "
        "Nunca prescreva diretamente; indique que a conduta exige VALIDAÇÃO MÉDICA.\n\n"
        f"PROTOCOLOS:\n{proto_txt}\n\n"
    )
    if state.get("patient_context"):
        prompt += f"CONTEXTO DO PACIENTE:\n{state['patient_context']}\n\n"
    prompt += f"PERGUNTA DO MÉDICO: {state['pergunta']}\n\nRESPOSTA (cite as fontes):"
    resposta = _llm.invoke(prompt)
    fontes = sorted({p["fonte"] for p in state["protocolos"]})
    return {"prompt": prompt, "resposta": resposta, "fontes": fontes}


def validacao_saida(state: AssistantState) -> AssistantState:
    r = guardrails.check_output(state["resposta"])
    resposta = state["resposta"] + r["selo"]
    resposta += "\n\n📎 Fontes: " + (", ".join(state["fontes"]) if state["fontes"] else "nenhuma")
    return {"resposta": resposta, "needs_human_validation": r["needs_human_validation"]}


def auditoria(state: AssistantState) -> AssistantState:
    audit.log_event(
        pergunta=state["pergunta"],
        resposta=state["resposta"],
        patient_id=state.get("patient_id"),
        fontes=state.get("fontes", []),
        blocked=state.get("blocked", False),
        needs_human_validation=state.get("needs_human_validation", False),
    )
    return {}


def _route_after_guardrail(state: AssistantState) -> str:
    return "bloquear" if state["blocked"] else "buscar_contexto"


def _bloquear(state: AssistantState) -> AssistantState:
    return {"resposta": state["block_message"], "fontes": []}


def build_graph(llm=None):
    """Compila o grafo. `llm` injetável (MockLLM em testes, HuggingFace em prod)."""
    global _llm
    if llm is not None:
        _llm = llm
    if _llm is None:
        from src.assistant.llm import load_llm
        _llm = load_llm()

    g = StateGraph(AssistantState)
    g.add_node("guardrail_entrada", guardrail_entrada)
    g.add_node("busca_contexto", busca_contexto)
    g.add_node("gera_resposta", gera_resposta)
    g.add_node("validacao_saida", validacao_saida)
    g.add_node("auditoria", auditoria)
    g.add_node("bloquear", _bloquear)

    g.add_edge(START, "guardrail_entrada")
    g.add_conditional_edges("guardrail_entrada", _route_after_guardrail,
                            {"buscar_contexto": "busca_contexto", "bloquear": "bloquear"})
    g.add_edge("busca_contexto", "gera_resposta")
    g.add_edge("gera_resposta", "validacao_saida")
    g.add_edge("validacao_saida", "auditoria")
    g.add_edge("bloquear", "auditoria")
    g.add_edge("auditoria", END)
    return g.compile()


def run(pergunta: str, patient_id: int | None = None, llm=None) -> str:
    app = build_graph(llm)
    out = app.invoke({"pergunta": pergunta, "patient_id": patient_id})
    return out["resposta"]


if __name__ == "__main__":
    print(run("Qual a conduta inicial na sepse para o paciente?", patient_id=1))
