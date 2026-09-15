"""Tools de acesso ao prontuário (SQLite) expostas ao assistente."""
import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.config import DB_PATH


def _query(sql: str, params: tuple) -> list[dict]:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        return [dict(r) for r in conn.execute(sql, params).fetchall()]


def get_patient_summary(patient_id: int) -> dict | None:
    rows = _query("SELECT * FROM pacientes WHERE id = ?", (patient_id,))
    return rows[0] if rows else None


def get_patient_exams(patient_id: int, only_pending: bool = False) -> list[dict]:
    sql = "SELECT tipo, resultado, status, data FROM exames WHERE paciente_id = ?"
    params: tuple = (patient_id,)
    if only_pending:
        sql += " AND status = 'pendente'"
    return _query(sql, params)


def patient_context_text(patient_id: int) -> str:
    """Contexto estruturado do paciente para injetar no prompt (RAG estruturado)."""
    p = get_patient_summary(patient_id)
    if not p:
        return f"Paciente {patient_id} não encontrado."
    exams = get_patient_exams(patient_id)
    pending = [e for e in exams if e["status"] == "pendente"]
    lines = [
        f"Paciente {p['id']}: {p['idade']} anos, sexo {p['sexo']}.",
        f"Alergias: {p['alergias']}. Comorbidades: {p['comorbidades']}.",
        "Exames concluídos: " + ("; ".join(f"{e['tipo']}: {e['resultado']} ({e['data']})" for e in exams if e["status"] == "concluido") or "nenhum"),
        "Exames PENDENTES: " + ("; ".join(f"{e['tipo']} ({e['data']})" for e in pending) or "nenhum"),
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    print(patient_context_text(1))
