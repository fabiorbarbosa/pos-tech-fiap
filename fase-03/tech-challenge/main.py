#!/usr/bin/env python3
"""CLI do assistente médico.

Exemplos:
    python main.py --question "Qual a conduta na sepse?" --patient-id 1
    python main.py --mock --question "Prescreva 40 mg de enoxaparina"
    python main.py --demo            # cenário completo de demonstração (mock)
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

QUESTION_DEMO = "Quais exames pendentes e conduta para o paciente 1 com suspeita de SCA?"

DEMO_CENARIOS = [
    ("Qual a conduta inicial na sepse?", 1, "conduta em protocolo + contexto do paciente"),
    ("Prescreva enoxaparina 40 mg para o paciente 1.", 1, "guardrail: bloqueio de prescrição direta"),
    ("Quais exames estão pendentes para o paciente 1?", 1, "RAG estruturado sobre prontuário"),
]


def demo(llm) -> None:
    print("\n" + "=" * 70 + "\nDEMO — assistente médico (dados sintéticos)\n" + "=" * 70)
    for q, pid, label in DEMO_CENARIOS:
        print(f"\n--- Cenário: {label} ---")
        print(f"Pergunta (paciente {pid}): {q}")
        from src.assistant.graph import run
        print(run(q, patient_id=pid, llm=llm))
    print(f"\nLog de auditoria em logs/audit.jsonl")


def main() -> None:
    ap = argparse.ArgumentParser(description="Assistente médico com LangGraph")
    ap.add_argument("--question", "-q", help="Pergunta clínica")
    ap.add_argument("--patient-id", "-p", type=int, default=None, help="ID do paciente (contexto de prontuário)")
    ap.add_argument("--mock", action="store_true", help="Usa LLM mock (sem download/GPU)")
    ap.add_argument("--demo", action="store_true", help="Roda cenários de demonstração")
    args = ap.parse_args()

    if args.mock:
        os.environ["LLM_MODE"] = "mock"

    from src.assistant.llm import MockLLM, load_llm
    llm = MockLLM() if args.mock else load_llm()

    if args.demo:
        demo(llm)
    elif args.question:
        from src.assistant.graph import run
        print(run(args.question, patient_id=args.patient_id, llm=llm))
    else:
        ap.print_help()
        print("\nExemplo: python main.py --mock -q \"Qual a conduta na sepse?\" -p 1")


if __name__ == "__main__":
    main()
