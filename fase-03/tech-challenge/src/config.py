"""Configurações centrais do projeto."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_SEED = ROOT / "data" / "seed"
DATA_PROCESSED = ROOT / "data" / "processed"
DB_PATH = ROOT / "data" / "medical_assistant.db"
LOGS_DIR = ROOT / "logs"
MODELS_DIR = ROOT / "models"
ADAPTER_PATH = MODELS_DIR / "qlora_adapter"

# LLM base pequena para fine-tuning QLoRA e inferência local (CPU ok)
BASE_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"

# RAG
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
FAISS_DIR = MODELS_DIR / "faiss_index"
RAG_TOP_K = 3

DISCLAIMER = (
    "\n\n⚠️ Aviso: resposta gerada por assistente de IA de apoio à decisão. "
    "Não substitui julgamento clínico. Toda conduta deve ser validada por médico responsável."
)

for d in (DATA_PROCESSED, LOGS_DIR, MODELS_DIR):
    d.mkdir(parents=True, exist_ok=True)
