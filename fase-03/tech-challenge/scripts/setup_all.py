#!/usr/bin/env python3
"""Setup completo: dataset + banco + índice RAG. Rode uma vez antes de usar o assistente."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STEPS = [
    ("Dataset de fine-tuning", [sys.executable, "-m", "src.data_prep.build_dataset"]),
    ("Banco SQLite (prontuários)", [sys.executable, "-m", "src.db.init_db"]),
    ("Índice FAISS dos protocolos", [sys.executable, "-m", "src.assistant.rag"]),
]

for label, cmd in STEPS:
    print(f"\n=== {label} ===")
    subprocess.run(cmd, cwd=ROOT, check=True)

print("\nSetup concluído. Rode: python main.py --demo")
