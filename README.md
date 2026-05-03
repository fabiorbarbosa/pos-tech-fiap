# Pós Tech - 9IADT - IA para Devs

## Tech Challenge B

## Problema

Este projeto propõe uma solução inicial de apoio à triagem médica por meio de classificação binária para indicativo de diabetes, utilizando dados clínicos tabulares.

## Dataset

- Nome: `Diabetes Dataset`
- Fonte: [Kaggle - mathchi/diabetes-data-set](https://www.kaggle.com/datasets/mathchi/diabetes-data-set/data)
- Arquivo utilizado: [dataset/diabetes.csv](./dataset/diabetes.csv)
- Variável-alvo: `Outcome`

## Objetivo da solução

Treinar e avaliar modelos de Machine Learning capazes de prever a variável `Outcome` a partir de atributos clínicos como glicose, pressão arterial, insulina, IMC e idade.

## Estrutura do repositório

- [dataset](./dataset): base utilizada no projeto.
- [notebooks](./notebooks): notebooks finais da análise e da modelagem.
- [figures](./figures): espaço para gráficos exportados.
- [results](./results): espaço para tabelas e artefatos finais.
- [Dockerfile](./Dockerfile): ambiente reprodutível para execução.

## Notebooks principais

- [01-exploracao-e-preprocessamento-final.ipynb](./notebooks/01-exploracao-e-preprocessamento-final.ipynb)
- [02-modelagem-avaliacao-e-interpretabilidade-final.ipynb](./notebooks/02-modelagem-avaliacao-e-interpretabilidade-final.ipynb)

## Como executar localmente

1. Crie um ambiente virtual Python 3.12.
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Abra o Jupyter Lab ou Jupyter Notebook:

```bash
jupyter lab
```

4. Execute os notebooks na ordem:

```text
1. 01-exploracao-e-preprocessamento-final.ipynb
2. 02-modelagem-avaliacao-e-interpretabilidade-final.ipynb
```

## Como executar com Docker

1. Construa a imagem:

```bash
docker build -t tech-challenge-b .
```

2. Rode o container:

```bash
docker run --rm -it -p 8888:8888 tech-challenge-b
```

3. Acesse o Jupyter Lab em `http://localhost:8888`.

## Principais resultados esperados

- análise exploratória com identificação de zeros clinicamente suspeitos;
- estratégia de pré-processamento reproduzível;
- comparação entre pelo menos dois modelos de classificação;
- avaliação com `accuracy`, `recall` e `F1-score`;
- matriz de confusão;
- interpretabilidade com importância das variáveis e discussão crítica.

## Observações

- O uso proposto é de apoio à triagem, e não de substituição da decisão médica.
- Os resultados devem ser interpretados à luz das limitações do dataset e do contexto acadêmico do experimento.
