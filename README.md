# Pós Tech FIAP - IA para Devs

Este repositório organiza os entregáveis, estudos e projetos desenvolvidos ao longo da pós-graduação **IA para Devs**, da **FIAP**.

## Sobre a pós-graduação

De acordo com a descrição oficial do curso, a pós é voltada para desenvolvimento de soluções com Inteligência Artificial, Machine Learning, NLP, GenAI, LLMs e serviços em nuvem. A jornada é dividida em **5 fases**, o **Tech Challenge** funciona como o projeto principal da formação, evoluindo fase após fase.

De forma resumida, a trilha inclui:

- fundamentos de Inteligência Artificial e Machine Learning;
- visão computacional;
- processamento de linguagem natural;
- desenvolvimento de ML em nuvem;
- LLMs, OpenAI, LangChain e LangGraph;
- análise de dados multimodais;
- privacidade, segurança de dados e aplicações práticas.

## Estrutura do repositório

Este repositório foi organizado para acompanhar a evolução da pós ao longo das cinco fases.

```text
.
├── fase-01/
│   └── tech-challenge/
├── fase-02/
│   └── tech-challenge/
├── fase-03/
├── fase-04/
└── fase-05/
```

### Convenção adotada

- Cada diretório `fase-0X` representa uma fase da pós.
- Dentro de cada fase podem existir:
  - `tech-challenge/`
  - `atividades/`
  - `anotacoes/`
  - `projetos/`
- O material pode incluir:
  - notebooks;
  - relatórios técnicos;
  - datasets ou links para obtenção dos dados;
  - resultados exportados;
  - arquivos de execução, como `README.md`, `Dockerfile` e `requirements.txt`.

## Status atual do repositório

No momento, o material consolidado neste repositório corresponde às **Fases 1 e 2**, nos diretórios:

- [fase-01/tech-challenge](./fase-01/tech-challenge)
- [fase-02/tech-challenge](./fase-02/tech-challenge)

Esses diretórios contêm as entregas completas do **Tech Challenge B**, com notebooks finais, relatórios técnicos, datasets, resultados exportados e ambiente reprodutível.

## Fase 1 - Tech Challenge B

O projeto da Fase 1 foi desenvolvido com foco em **classificação binária de indicativo de diabetes** a partir de dados clínicos tabulares.

### Conteúdo principal

- exploração e pré-processamento dos dados;
- modelagem com comparação entre algoritmos;
- avaliação com métricas adequadas ao contexto do problema;
- análise de matriz de confusão;
- interpretabilidade com importância das variáveis e SHAP;
- discussão crítica sobre uso prático e limitações.

### Acesso rápido

- [README da Fase 1](./fase-01/tech-challenge/README.md)
- [Relatório técnico em Markdown](./fase-01/tech-challenge/relatorio-tecnico.md)
- [Relatório técnico em PDF](./fase-01/tech-challenge/relatorio-tecnico-final.pdf)
- [Notebooks](./fase-01/tech-challenge/notebooks)

## Fase 2 - Tech Challenge B

O projeto da Fase 2 foi desenvolvido com foco em **otimização de rotas para distribuição de medicamentos e insumos** com uso de **algoritmo genético** e geração de artefatos textuais com apoio de **LLMs**.

### Conteúdo principal

- adaptação do `Amazon Delivery Dataset` para o contexto médico;
- modelagem de roteirização multi-veículo com restrições de capacidade, autonomia e prioridade;
- comparação entre experimentos com diferentes configurações do algoritmo genético;
- visualização das rotas otimizadas e da convergência do algoritmo;
- geração de instruções operacionais, relatório operacional e prompt para LLM;
- discussão crítica sobre limitações da base e da modelagem adotada.

### Acesso rápido

- [README da Fase 2](./fase-02/tech-challenge/README.md)
- [Relatório técnico em Markdown](./fase-02/tech-challenge/relatorio-tecnico.md)
- [Notebooks](./fase-02/tech-challenge/notebooks)
- [Resultados](./fase-02/tech-challenge/results)
- [Figuras](./fase-02/tech-challenge/figures)

## Objetivo deste repositório

O objetivo deste repositório é centralizar a produção da pós-graduação em um único lugar, permitindo:

- rastrear a evolução do Tech Challenge entre as fases;
- manter os artefatos organizados por contexto e período;
- facilitar consulta futura para portfólio;
- documentar a jornada de aprendizado com foco prático.

## Observações

- A estrutura foi pensada para crescer ao longo das próximas fases.
- Nem todos os diretórios das fases seguintes precisam existir imediatamente; eles podem ser criados conforme a jornada evoluir.
- O conteúdo da Fase 1 já está organizado em formato de entrega final.
