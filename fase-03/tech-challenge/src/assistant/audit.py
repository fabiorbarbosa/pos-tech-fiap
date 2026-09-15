"""Log de auditoria em JSONL — rastreabilidade de cada interação (LGPD/auditoria)."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.config import LOGS_DIR

AUDIT_FILE = LOGS_DIR / "audit.jsonl"


def log_event(
    pergunta: str,
    resposta: str,
    patient_id: int | None,
    fontes: list[str],
    blocked: bool,
    needs_human_validation: bool,
) -> None:
    LOGS_DIR.mkdir(exist_ok=True)
    event = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "patient_id": patient_id,
        "pergunta": pergunta,
        "resposta": resposta,
        "fontes_citadas": fontes,          # explainability
        "bloqueado_guardrail": blocked,
        "exige_validacao_humana": needs_human_validation,
    }
    with open(AUDIT_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    log_event("teste", "resposta", 1, ["PROT-001"], False, True)
    print(AUDIT_FILE.read_text(encoding="utf-8").strip().splitlines()[-1])
