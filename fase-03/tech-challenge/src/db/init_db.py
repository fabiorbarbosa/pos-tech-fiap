"""Cria o banco SQLite com prontuários e exames sintéticos (pacientes fictícios)."""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS pacientes (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,         -- fictício
    idade INTEGER,
    sexo TEXT,
    alergias TEXT,
    comorbidades TEXT
);
CREATE TABLE IF NOT EXISTS exames (
    id INTEGER PRIMARY KEY,
    paciente_id INTEGER REFERENCES pacientes(id),
    tipo TEXT,
    resultado TEXT,
    status TEXT,                -- pendente | concluido
    data TEXT
);
CREATE TABLE IF NOT EXISTS prescricoes (
    id INTEGER PRIMARY KEY,
    paciente_id INTEGER REFERENCES pacientes(id),
    medicamento TEXT,
    dose TEXT,
    validado_por TEXT,          -- médico responsável (obrigatório)
    data TEXT
);
"""

PACIENTES = [
    (1, "Paciente Alfa", 67, "M", "Penicilina", "HAS, DM2"),
    (2, "Paciente Beta", 54, "F", "Nenhuma", "FA, IC FEVE 35%"),
    (3, "Paciente Gama", 72, "M", "Sulfa", "DPOC, DRC est.3"),
    (4, "Paciente Delta", 45, "F", "Nenhuma", "Nenhuma"),
]

EXAMES = [
    (1, 1, "Hemograma", "Hb 11,2; leuco 12.400; plaquetas 210 mil", "concluido", "2026-09-01"),
    (2, 1, "Troponina", "Aguardando coleta", "pendente", "2026-09-08"),
    (3, 1, "ECG", "Ritmo sinusal, sem supra", "concluido", "2026-09-07"),
    (4, 2, "Ecocardiograma", "FEVE 35%, disfunção sistólica moderada", "concluido", "2026-08-30"),
    (5, 2, "Creatinina", "1,1 mg/dL", "concluido", "2026-09-05"),
    (6, 3, "Gasometria", "pH 7,38; pCO2 48; pO2 62", "concluido", "2026-09-06"),
    (7, 3, "Raio-X tórax", "Aguardando agendamento", "pendente", "2026-09-08"),
    (8, 4, "HbA1c", "6,4%", "concluido", "2026-08-20"),
]

PRESCRICOES = [
    (1, 1, "Enoxaparina", "40 mg SC 1x/dia", "Dr. Responsável A (CRM 000000)", "2026-09-07"),
    (2, 2, "Furosemida", "40 mg IV 12/12h", "Dra. Responsável B (CRM 000001)", "2026-09-08"),
]


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(SCHEMA)
        conn.executemany("INSERT OR REPLACE INTO pacientes VALUES (?,?,?,?,?,?)", PACIENTES)
        conn.executemany("INSERT OR REPLACE INTO exames VALUES (?,?,?,?,?,?)", EXAMES)
        conn.executemany("INSERT OR REPLACE INTO prescricoes VALUES (?,?,?,?,?,?)", PRESCRICOES)
    print(f"Banco criado: {DB_PATH} ({len(PACIENTES)} pacientes)")


if __name__ == "__main__":
    init_db()
