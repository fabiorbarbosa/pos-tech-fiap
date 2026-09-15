# Pós Tech - 9IADT - IA para Devs

## Tech Challenge - Fase 3

# Assistente Médico Virtual

Assistente virtual médico treinado com dados próprios do hospital (sintéticos),
que auxilia em condutas clínicas, consulta prontuários e sugere procedimentos
com base em protocolos internos — orquestrado por **LangChain/LangGraph** e com
**fine-tuning QLoRA** de LLM.

## Requisitos atendidos

| Requisito | Onde |
|---|---|
| Fine-tuning de LLM com dados médicos | `src/fine_tuning/train.py`, `notebooks/finetuning_colab.ipynb` |
| Preprocessing, anonimização e curadoria | `src/data_prep/` (LGPD, dedup, split holdout) |
| Pipeline LangChain com LLM customizada | `src/assistant/graph.py`, `src/assistant/llm.py` |
| Consulta a base estruturada (prontuários) | `src/db/init_db.py`, `src/assistant/tools.py` (SQLite) |
| Contextualização com dados do paciente | `src/assistant/graph.py` (nó `busca_contexto`) |
| Limites de atuação (sem prescrição direta) | `src/assistant/guardrails.py` |
| Logging para auditoria | `src/assistant/audit.py` → `logs/audit.jsonl` |
| Explainability (citação de fonte) | `src/assistant/rag.py`, `validacao_saida` no grafo |
| Projeto modular em Python + README | este repositório |
| Dataset anonimizado/sintético | `data/seed/` |
| Fluxos LangGraph | `src/assistant/graph.py` |
| Relatório técnico | `reports/RELATORIO_TECNICO.md` |

## Estrutura

```
tech-challenge/
├── main.py                     # CLI do assistente
├── scripts/setup_all.py        # dataset + banco + índice RAG (1 comando)
├── notebooks/finetuning_colab.ipynb
├── src/
│   ├── config.py               # paths, modelo base, thresholds
│   ├── data_prep/              # anonimização + dataset JSONL de instruções
│   ├── db/                     # SQLite com pacientes/exames sintéticos
│   ├── fine_tuning/            # treino QLoRA + avaliação (ROUGE-L)
│   └── assistant/
│       ├── llm.py              # base / fine-tunado / mock
│       ├── rag.py              # RAG sobre protocolos (FAISS, fallback lexical)
│       ├── tools.py            # consultas ao prontuário
│       ├── guardrails.py       # limites de atuação
│       ├── audit.py            # log JSONL por interação
│       └── graph.py            # fluxo LangGraph (nós + arestas condicionais)
├── data/seed/                  # protocolos, FAQ, templates (sintéticos)
├── tests/test_smoke.py         # testes offline (sem GPU/rede)
├── results/                    # métricas finais e evidências de execução
├── figures/                    # visualização final da avaliação
├── relatorio-tecnico.md        # relatório técnico da entrega
└── roteiro-video.md             # roteiro para a apresentação
```

## Instalação

Recomendado: `python -m venv .venv && source .venv/bin/activate`.

```bash
pip install -r requirements.txt
```

> No macOS `bitsandbytes` não é instalado (QLoRA exige CUDA). Fine-tuning roda no
> Colab (ver `notebooks/`). O assistente em modo `mock` e o demo funcionam em
> qualquer máquina.

## Como executar

```bash
# 1) Setup: dataset anonimizado + banco SQLite + índice RAG
python scripts/setup_all.py

# 2) Demo completa (modo mock, sem download/GPU)
python main.py --mock --demo

# 3) Pergunta única com contexto de paciente (mock)
python main.py --mock -q "Quais exames pendentes para o paciente 1?" -p 1

# 4) Com modelo real (HuggingFace, CPU ok): baixa Qwen2.5-0.5B-Instruct
python main.py -q "Qual a conduta na sepse?" -p 1

# 5) Com o modelo fine-tunado (após treinar):
LLM_MODE=auto python main.py -q "Qual a conduta na sepse?" -p 1

# 6) Smoke tests (offline)
python tests/test_smoke.py
```

## Fine-tuning (GPU/Colab)

O treino usa **QLoRA** sobre `Qwen/Qwen2.5-0.5B-Instruct` com o dataset de
instruções gerado dos protocolos/FAQ/templates internos.

```bash
python -m src.data_prep.build_dataset        # gera data/processed/*.jsonl (41 treino / 10 eval)
python -m src.fine_tuning.train --dry-run    # valida dados + tokenização (sem GPU)
python -m src.fine_tuning.train --epochs 3   # treina (GPU/Colab QLoRA) → models/qlora_adapter
python -m src.fine_tuning.train --no-quant --epochs 3   # Apple Silicon (LoRA full-precision em MPS)
python -m src.fine_tuning.evaluate --variant ambos   # base vs fine-tunado
```

No Colab (GPU) use o notebook `notebooks/finetuning_colab.ipynb` (Runtime → T4,
roda QLoRA 4-bit). Localmente em Apple Silicon use `--no-quant` (LoRA em MPS,
~2 min no M1 Pro).

**Avaliação final registrada:** ROUGE-L médio **0,0933** e taxa de citação de
fonte **80%** no holdout de 10 itens. Resultados completos estão em
`results/eval_results_final.json`, com visualização em `figures/`.

## Guardrails (limites de atuação)

1. **Nunca prescreve diretamente** — pedidos de prescrição/ajuste são bloqueados
   na entrada (`guardrails.check_input`).
2. **Sem receita assinada** — saídas que mencionam dose/posologia recebem selo
   "VALIDAÇÃO MÉDICA OBRIGATÓRIA" (`check_output`).
3. **Emergências com risco de vida** — redireciona para atendimento imediato.
4. **Explainability** — toda resposta cita as fontes (`PROT-XXX`) usadas.
5. **Auditoria** — cada interação vira uma linha JSON em `logs/audit.jsonl`.

## Vídeo de demonstração (roteiro)

Trecho para o vídeo (≤15 min), tudo com `--mock` ou modelo fine-tunado:

1. **Preparação** — `python scripts/setup_all.py` (mostra anonimização e dataset).
2. **Fine-tuning** — `python -m src.fine_tuning.train --dry-run` (valida pipeline).
3. **Fluxo automatizado** — `python main.py --mock --demo` (3 cenários).
4. **Pergunta contextualizada** — `-q "conduta na sepse?" -p 1` (mostra prontuário
   no contexto e fontes citadas).
5. **Guardrail** — `-q "Prescreva 40 mg de enoxaparina"` (bloqueio).
6. **Logs** — `cat logs/audit.jsonl` (auditoria por interação).

## Entregáveis presentes

- código-fonte, testes e dados sintéticos para reprodução;
- notebook de fine-tuning e adaptador LoRA treinado;
- relatório técnico em Markdown e PDF;
- métricas finais e visualização da avaliação;
- Dockerfile para executar o demo offline.

## Pendências manuais

- publicar o vídeo gravado a partir de `roteiro-video.md`;
- preencher, se solicitado pela instituição, o link final do repositório e do vídeo.
