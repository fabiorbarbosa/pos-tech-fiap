"""RAG sobre protocolos internos: índice FAISS + busca com citação de fonte."""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.config import DATA_SEED, EMBEDDING_MODEL, FAISS_DIR, RAG_TOP_K

_store = None


def build_index() -> None:
    from langchain_community.vectorstores import FAISS
    from langchain_huggingface import HuggingFaceEmbeddings

    protocols = json.loads((DATA_SEED / "protocols.json").read_text(encoding="utf-8"))
    texts = [f"{p['titulo']}\n{p['conteudo']}" for p in protocols]
    metas = [{"fonte": p["id"], "titulo": p["titulo"]} for p in protocols]
    emb = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    store = FAISS.from_texts(texts, emb, metadatas=metas)
    FAISS_DIR.mkdir(parents=True, exist_ok=True)
    store.save_local(str(FAISS_DIR))
    print(f"Índice FAISS salvo em {FAISS_DIR} ({len(texts)} protocolos)")


def _get_store():
    global _store
    if _store is None:
        from langchain_community.vectorstores import FAISS
        from langchain_huggingface import HuggingFaceEmbeddings
        if not FAISS_DIR.exists():
            build_index()
        emb = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        _store = FAISS.load_local(str(FAISS_DIR), emb, allow_dangerous_deserialization=True)
    return _store


def _keyword_search(query: str, k: int) -> list[dict]:
    """Fallback lexical — ponytail: deixa a demo rodar sem FAISS/embeddings."""
    protocols = json.loads((DATA_SEED / "protocols.json").read_text(encoding="utf-8"))
    q = set(query.lower().split())

    def score(p: dict) -> int:
        hay = f"{p['titulo']} {p['conteudo']} {' '.join(p.get('tags', []))}".lower()
        return sum(1 for w in q if len(w) > 3 and w in hay)

    top = sorted(protocols, key=score, reverse=True)[:k]
    return [{"fonte": p["id"], "titulo": p["titulo"], "trecho": f"{p['titulo']}\n{p['conteudo']}"}
            for p in top if score(p) > 0] or [
        {"fonte": protocols[0]["id"], "titulo": protocols[0]["titulo"],
         "trecho": f"{protocols[0]['titulo']}\n{protocols[0]['conteudo']}"}
    ]


def search_protocols(query: str, k: int = RAG_TOP_K) -> list[dict]:
    """Retorna [{'fonte', 'titulo', 'trecho'}] — fonte sempre incluída (explainability)."""
    if os.getenv("LLM_MODE") == "mock":
        return _keyword_search(query, k)
    try:
        docs = _get_store().similarity_search(query, k=k)
        return [
            {"fonte": d.metadata["fonte"], "titulo": d.metadata["titulo"], "trecho": d.page_content}
            for d in docs
        ]
    except (ImportError, OSError, RuntimeError):
        return _keyword_search(query, k)


if __name__ == "__main__":
    build_index()
