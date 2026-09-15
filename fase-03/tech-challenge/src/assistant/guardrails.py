"""Guardrails: limites de atuação do assistente.

Regras:
  1. NUNCA prescrever/ajustar dose diretamente -> bloqueado na entrada;
  2. Sem diagnóstico definitivo de emergência sem contexto mínimo;
  3. Toda saída que mencionar prescrição recebe selo de VALIDAÇÃO HUMANA;
  4. Emergência com risco de vida -> orientar atendimento imediato.
"""
import re

BLOCK_PATTERNS = [
    (re.compile(r"\b(prescrev[ae]|receite|assin[ae])\b.*\b(mg|ml|dose|medica|receita)\b", re.I | re.S),
     "Prescrição direta não é permitida. Posso sugerir condutas de protocolo para validação médica."),
    (re.compile(r"\b(pare|suspenda|interrompa)\b.*\b(medicamento|antibiótico|droga|sedativo)\b", re.I),
     "Suspensão de medicação exige avaliação do médico assistente. Escalando."),
]

VALIDATION_PATTERNS = re.compile(
    r"\b(prescri|receitu[aá]rio|posologia|\d+\s?mg\b|administre|iniciar\s+\w+\s+\d)", re.I
)

RISK_REDIRECT = re.compile(r"\b(parada card[ií]aca|n[aã]o respira|inconsciente|engasg)\b", re.I)


def check_input(question: str) -> dict:
    """Retorna {'blocked': bool, 'message': str|None}."""
    if RISK_REDIRECT.search(question):
        return {
            "blocked": True,
            "message": ("Sinais de emergência com risco de vida detectados. Acione a equipe de "
                        "emergência / atendimento imediato. Este assistente não substitui suporte de vida."),
        }
    for rx, msg in BLOCK_PATTERNS:
        if rx.search(question):
            return {"blocked": True, "message": msg}
    return {"blocked": False, "message": None}


def check_output(answer: str) -> dict:
    """Pós-verificação: marca respostas que exigem validação humana."""
    needs = bool(VALIDATION_PATTERNS.search(answer))
    return {
        "needs_human_validation": needs,
        "selo": "\n\n🔒 VALIDAÇÃO MÉDICA OBRIGATÓRIA antes de qualquer prescrição/conduta." if needs else "",
    }


if __name__ == "__main__":  # verificação rápida
    assert check_input("Prescreva enoxaparina 40 mg agora")["blocked"]
    assert check_input("O paciente está inconsciente e não respira")["blocked"]
    assert not check_input("Qual a conduta na sepse?")["blocked"]
    assert check_output("Iniciar ceftriaxona 1 g IV")["needs_human_validation"]
    assert not check_output("Caminhar é saudável.")["needs_human_validation"]
    print("guardrails OK")
