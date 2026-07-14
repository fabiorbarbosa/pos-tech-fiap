# Pos Tech - 9IADT - IA para Devs

## Tech Challenge - Fase 2

## Projeto escolhido

Projeto 2: otimização de rotas para distribuição de medicamentos e insumos com algoritmo genético e apoio de LLMs.

## Objetivo

O projeto implementa um fluxo de roteirização médica com múltiplos veículos, restrições de capacidade e autonomia, prioridades de entrega e geração de artefatos textuais para apoio operacional.

## Base utilizada

- Base principal da entrega: `Amazon Delivery Dataset`, adaptado para o contexto médico.
- Base convertida para o projeto: `dataset/converted/stops_from_amazon.csv` e `dataset/converted/vehicles_from_amazon.csv`.
- Amostra final usada nos experimentos e no script principal: `dataset/samples/stops_sample_100.csv` e `dataset/samples/vehicles_sample_100_experiment.csv`.
- Fixtures mínimas para testes de conversão: `dataset/public/amazon_delivery_sample.csv` e `dataset/public/uhhc_A1.json`.

## Estrutura

- [src](./src): código-fonte do otimizador, conversores, relatórios e visualização.
- [tests](./tests): testes automatizados.
- [notebooks](./notebooks): notebooks finais da entrega.
- [dataset](./dataset): bases mínimas para reprodução dos experimentos e testes.
- [results](./results): instruções, relatório operacional e prompt final.
- [figures](./figures): visualizações finais exportadas.
- [relatorio-tecnico.md](./relatorio-tecnico.md): relatório técnico da entrega.

## Execução principal

Crie um ambiente virtual Python 3.12 e instale as dependências:

```bash
pip install -r requirements.txt
```

Rode os testes:

```bash
PYTHONPATH=src python -m pytest
```

Execute o experimento final da entrega:

```bash
PYTHONPATH=src python run_demo.py
```

Esse script usa a mesma amostra final e os mesmos hiperparâmetros consolidados nos notebooks:

- `population_size=120`
- `generations=120`
- `mutation_rate=0.10`
- `elite_size=2`
- `random_seed=42`

Na execução consolidada, o script reproduz os resultados finais documentados nos notebooks e no relatório técnico, incluindo `fitness = 31519.00` e `distance = 605.70`.

Saídas geradas:

- `results/driver_instructions_final.md`
- `results/operations_report_final.md`
- `results/llm_prompt_final.txt`
- `figures/rotas-otimizadas-final-clean.png`
- `figures/convergencia-ga-final.png`

## Ordem dos notebooks

```text
1. 01-entendimento-do-problema-final.ipynb
2. 02-modelagem-genetica-final.ipynb
3. 03-avaliacao-e-visualizacao-final.ipynb
4. 04-llm-relatorios-final.ipynb
```

## Entregáveis presentes

- código-fonte completo;
- testes automatizados;
- notebooks de demonstração;
- relatório técnico;
- visualizações finais;
- artefatos de instruções e relatório com apoio de LLM.

## Pendências manuais

- preencher links finais de repositório e vídeo no relatório técnico;
- publicar o vídeo de demonstração no YouTube ou Vimeo.
