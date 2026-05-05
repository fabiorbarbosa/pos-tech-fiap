# Relatório Técnico - Tech Challenge B

## Solução de IA para apoio à triagem de indicativo de diabetes com Machine Learning

**Pós-graduação:** IA para Devs  
**Instituição:** FIAP + Alura  
**Fase:** Fase 1  
**Desafio:** Tech Challenge B  

**Integrante:**  
- Fábio Rodrigues Barbosa

**Data:** 03/05/2026

## Links da entrega

Os artefatos principais deste projeto podem ser acessados nos links abaixo:

- **Repositório Git:** [https://github.com/fabiorbarbosa/tech-challenge-01](https://github.com/fabiorbarbosa/tech-challenge-01)
- **Vídeo de demonstração:** [https://vimeo.com/1189213606](https://vimeo.com/1189213606)
<div style="page-break-after: always;"></div>

## 1. Introdução

Este projeto apresenta uma solução inicial de Inteligência Artificial aplicada ao apoio à triagem médica, com foco na classificação binária de indicativo de diabetes a partir de dados clínicos tabulares.

O problema foi modelado como uma tarefa de classificação supervisionada, em que o objetivo é prever a variável `Outcome`, indicando se a paciente pertence à classe com indicativo positivo de diabetes (`1`) ou não (`0`).

A proposta está alinhada ao contexto de apoio à análise inicial de exames e dados médicos, sem substituir a decisão clínica profissional.

## 2. Definição do problema

O problema escolhido foi a predição de indicativo de diabetes com base em variáveis clínicas e demográficas. Em termos práticos, a solução busca responder se atributos como glicose, pressão arterial, insulina, IMC, idade e histórico familiar permitem distinguir pacientes com maior probabilidade de apresentar diabetes.

Trata-se de uma tarefa de classificação binária em saúde, na qual o impacto dos erros deve ser analisado com cuidado. Em particular, falsos negativos são mais sensíveis, pois podem deixar de sinalizar pacientes potencialmente positivos para investigação adicional.

## 3. Dataset utilizado

- Nome: `Diabetes Dataset`
- Fonte: [Kaggle - mathchi/diabetes-data-set](https://www.kaggle.com/datasets/mathchi/diabetes-data-set/data)
- Arquivo utilizado: `diabetes.csv`
- Variável-alvo: `Outcome`

O dataset contém 768 registros e 9 colunas, sendo 8 variáveis preditoras e 1 variável-alvo. As variáveis principais incluem:

- `Pregnancies`
- `Glucose`
- `BloodPressure`
- `SkinThickness`
- `Insulin`
- `BMI`
- `DiabetesPedigreeFunction`
- `Age`
- `Outcome`

O uso desse dataset foi escolhido por sua clareza estrutural, ampla utilização em estudos educacionais de Machine Learning e boa adequação ao problema proposto.

## 4. Exploração dos dados

Na inspeção inicial, verificou-se que a base não possui valores nulos formais nem registros duplicados. Ainda assim, a análise exploratória mostrou que parte das variáveis apresenta zeros clinicamente suspeitos, o que indica inconsistências semânticas nos dados.

A distribuição da variável-alvo mostrou desbalanceamento moderado, com predominância da classe negativa. Esse comportamento justificou o uso de métricas além da acurácia nas etapas de modelagem.

A Figura 1 apresenta a distribuição da variável-alvo.

<!-- ![Distribuição da variável-alvo](./figures/distribuicao-outcome.png) -->
<img src="./figures/distribuicao-outcome.png" width="80%">
<div style="page-break-after: always;"></div>

A Tabela 1 apresenta a distribuição da variável `Outcome`, mostrando a proporção entre pacientes sem indicativo e com indicativo de diabetes.

**Tabela 1. Distribuição da variável-alvo (`target-summary.csv`)**

| Outcome | Contagem | Percentual (%) |
|---|---:|---:|
| 0 | 500 | 65,10 |
| 1 | 268 | 34,90 |

As estatísticas descritivas mostraram diferenças relevantes de escala entre os atributos, além da presença de valores mínimos iguais a zero em variáveis clínicas como `Glucose`, `BloodPressure`, `SkinThickness`, `Insulin` e `BMI`, sugerindo possível ocorrência de valores ausentes disfarçados.

A análise de zeros suspeitos destacou principalmente as variáveis `Insulin` e `SkinThickness`, que concentraram as maiores proporções de valores iguais a zero. Esse resultado reforça a interpretação de que parte desses registros pode representar ausência de medição, e não observações clínicas reais.

**Tabela 2. Quantidade e percentual de zeros suspeitos (`zero-summary.csv`)**

| Variável | Zeros | Percentual de zeros (%) |
|---|---:|---:|
| Insulin | 374 | 48,70 |
| SkinThickness | 227 | 29,56 |
| BloodPressure | 35 | 4,56 |
| BMI | 11 | 1,43 |
| Glucose | 5 | 0,65 |

Também foi observada coerência entre a análise exploratória e a leitura visual das distribuições: variáveis como `Glucose` e `BMI` apresentaram comportamento mais estável, enquanto `Insulin` mostrou maior assimetria, concentração de zeros e sensibilidade a valores extremos.

Além disso, a matriz de correlação indicou que `Glucose` apresenta a relação linear mais forte com a variável-alvo, seguida por `BMI`, `Age` e `Pregnancies`. As magnitudes observadas não sugerem multicolinearidade extrema entre os atributos.
<div style="page-break-after: always;"></div>

A Figura 2 apresenta a matriz de correlação entre os atributos numéricos da base.

<!-- ![Matriz de correlação](./figures/matriz-correlacao.png) -->
<img src="./figures/matriz-correlacao.png" width="80%">

## 5. Pré-processamento

Com base na análise exploratória, foi definida uma estratégia de pré-processamento voltada à consistência metodológica e à adequação clínica dos dados para a modelagem.

As principais decisões adotadas foram:

- separação entre variáveis preditoras e variável-alvo;
- tratamento de zeros suspeitos como valores ausentes nas colunas `Glucose`, `BloodPressure`, `SkinThickness`, `Insulin` e `BMI`;
- manutenção de `Pregnancies` sem esse tratamento, pois o valor zero pode ser clinicamente válido;
- imputação de valores ausentes por mediana;
- padronização das variáveis numéricas;
- encapsulamento do fluxo em pipeline para evitar vazamento de dados.

A imputação por mediana foi escolhida por sua maior robustez frente a assimetrias e valores extremos, especialmente em variáveis como `Insulin`. Já a padronização foi aplicada para lidar com diferenças relevantes de escala entre os atributos, favorecendo modelos sensíveis à magnitude das variáveis.

Além disso, os dados foram divididos em conjuntos de treino e teste com estratificação pela variável-alvo, preservando a proporção original das classes e garantindo maior consistência na etapa de avaliação.

## 6. Modelagem

Foram comparados dois modelos de classificação supervisionada:

- `LogisticRegression`
- `RandomForest`

A regressão logística foi utilizada como baseline por sua simplicidade, interpretabilidade e uso frequente em problemas de classificação binária. Já o modelo `RandomForest` foi escolhido por sua capacidade de capturar relações não lineares e apresentar boa robustez em problemas tabulares com múltiplos atributos numéricos.

Para garantir comparabilidade justa entre os modelos, ambos foram executados com o mesmo pipeline de pré-processamento, a mesma divisão entre treino e teste e o mesmo conjunto de variáveis preditoras. Dessa forma, a comparação de desempenho passou a refletir principalmente as diferenças entre os algoritmos, e não variações no tratamento dos dados.

## 7. Avaliação dos modelos

A avaliação dos modelos foi realizada com base nas métricas `accuracy`, `recall` e `F1-score`, considerando o conjunto de teste. Essas métricas foram escolhidas porque, em contexto de saúde, a acurácia não deve ser interpretada isoladamente. O `recall` da classe positiva é especialmente relevante, pois está relacionado à capacidade de identificar corretamente pacientes com indicativo de diabetes, enquanto o `F1-score` contribui para avaliar o equilíbrio entre detecção de casos positivos e controle de erros.

A Tabela 3 apresenta os resultados obtidos pelos modelos avaliados.

**Tabela 3. Resultados comparativos entre os modelos (`metricas-modelos.csv`)**

| Modelo | Accuracy | Recall | F1-score |
|---|---:|---:|---:|
| RandomForest | 0,77 | 0,61 | 0,65 |
| LogisticRegression | 0,71 | 0,50 | 0,55 |

Os resultados mostram que o modelo `RandomForest` apresentou desempenho superior ao da `LogisticRegression` em todas as métricas consideradas. Em especial, o ganho em `recall` foi tratado como fator decisivo, pois reduz o risco de deixar de identificar pacientes potencialmente positivos, aspecto mais sensível no problema analisado.

Assim, a avaliação quantitativa indica que a `RandomForest` oferece melhor equilíbrio entre desempenho global e capacidade de identificação correta da classe positiva.

## 8. Matriz de confusão e análise dos erros

A análise da matriz de confusão permite compreender com mais clareza como o modelo final se comporta em relação aos diferentes tipos de erro. No contexto deste problema, essa leitura é especialmente importante porque falsos negativos representam pacientes com possível indicativo de diabetes que deixariam de ser sinalizados para investigação adicional.

A Figura 3 apresenta a matriz de confusão do modelo `RandomForest`, enquanto a Tabela 4 resume seus componentes.

<!-- ![Matriz de confusão do modelo RandomForest](./figures/matriz-confusao-randomforest.png) -->
<img src="./figures/matriz-confusao-randomforest.png" width="80%">
<div style="page-break-after: always;"></div>

**Tabela 4. Componentes da matriz de confusão do modelo RandomForest (`matriz-confusao-randomforest.csv`)**

| Verdadeiro Negativo | Falso Positivo | Falso Negativo | Verdadeiro Positivo |
|---:|---:|---:|---:|
| 86 | 14 | 21 | 33 |

Os resultados mostram que o modelo obteve boa capacidade de identificar corretamente tanto casos negativos quanto positivos. Em especial, a quantidade de falsos negativos foi reduzida em relação ao modelo baseline, o que reforça a adequação do `RandomForest` ao contexto analisado. Embora ainda existam erros de classificação, o comportamento observado indica melhor equilíbrio entre sensibilidade e desempenho global, aspecto importante para aplicações de apoio à triagem.

## 9. Interpretabilidade

A interpretabilidade do modelo final foi analisada com base na importância das variáveis e em visualizações com SHAP, com o objetivo de verificar se os sinais utilizados na predição são coerentes com o contexto clínico do problema.

A Tabela 5 apresenta a importância das variáveis no modelo `RandomForest`, enquanto a Figura 4 mostra a visualização gráfica dessa relevância.

**Tabela 5. Importância das variáveis no modelo RandomForest (`importancia-variaveis-randomforest.csv`)**

| Variável | Importância |
|---|---:|
| Glucose | 0,27 |
| BMI | 0,16 |
| DiabetesPedigreeFunction | 0,12 |
| Age | 0,11 |
| Insulin | 0,09 |
| BloodPressure | 0,08 |
| Pregnancies | 0,08 |
| SkinThickness | 0,07 |

<!-- ![Importância das variáveis no modelo RandomForest](./figures/importancia-variaveis-randomforest.png) -->
<img src="./figures/importancia-variaveis-randomforest.png" width="80%">

Os resultados mostram que `Glucose` foi a variável mais relevante para o modelo final, seguida por `BMI`, `DiabetesPedigreeFunction` e `Age`. Esse padrão é amplamente coerente com os achados da análise exploratória, especialmente no destaque anterior de `Glucose` e `BMI` como atributos com maior potencial discriminativo.

Além da importância global das variáveis, foi utilizada uma análise com SHAP para complementar a interpretação do comportamento do modelo. A Figura 5 apresenta a visualização-resumo dessa análise.

<!-- ![Resumo da interpretabilidade com SHAP](./figures/shap-summary-randomforest.png) -->
<img src="./figures/shap-summary-randomforest.png" width="80%">

A leitura conjunta dessas evidências reforça a consistência entre a etapa exploratória e a modelagem, sugerindo que o modelo se apoia em sinais clinicamente plausíveis, e não em padrões arbitrários ou de difícil justificativa.

Esse alinhamento entre análise exploratória e interpretabilidade fortalece a confiança nos resultados, pois sugere que o modelo está se apoiando em atributos clinicamente plausíveis.

## 10. Discussão crítica

Os resultados obtidos mostram que a solução possui potencial como ferramenta de apoio à triagem, especialmente pela capacidade do modelo final de identificar pacientes com indicativo positivo com desempenho superior ao baseline. Ainda assim, a interpretação dos resultados deve ser feita com cautela, considerando as limitações do experimento.

Uma das principais limitações está no próprio dataset utilizado, que representa um recorte populacional específico e relativamente pequeno. Esse fator reduz a capacidade de generalização dos resultados para outras populações e contextos clínicos. Além disso, a presença de zeros clinicamente suspeitos em variáveis relevantes exigiu tratamento no pré-processamento, o que reforça a existência de limitações de qualidade de dados.

Também é importante destacar que o desempenho observado se refere a uma base específica e a uma configuração experimental acadêmica, não devendo ser interpretado como validação clínica ampla. Embora o modelo `RandomForest` tenha apresentado melhor equilíbrio entre desempenho global e identificação de casos positivos, sua aplicação prática exigiria novas etapas de validação, inclusive em bases adicionais e em cenários operacionais distintos.

Assim, os resultados devem ser entendidos como evidência de viabilidade analítica da abordagem proposta, e não como solução pronta para implantação clínica.

## 11. Uso prático e implicações éticas

O uso mais adequado da solução proposta é como ferramenta de apoio à triagem ou à priorização de casos, e não como substituição da decisão médica. Em um cenário prático, o modelo poderia auxiliar profissionais de saúde a identificar pacientes com maior probabilidade de apresentar indicativo de diabetes, contribuindo para encaminhamentos, investigação complementar e organização do atendimento.

Ainda assim, qualquer aplicação em contexto real exigiria supervisão profissional contínua, uma vez que erros de classificação podem produzir impacto sobre pessoas reais. Nesse sentido, a interpretação dos resultados deve considerar limitações do dataset, risco de falsos negativos e necessidade de avaliação clínica complementar.

Do ponto de vista ético e operacional, também seria necessário observar requisitos de segurança, privacidade e confidencialidade dos dados, bem como princípios de uso responsável da informação em saúde. Dessa forma, o valor da solução está em apoiar a análise inicial de risco, preservando o papel central do profissional de saúde na decisão final.

## 12. Conclusão

O projeto mostrou que é possível construir uma solução inicial de Machine Learning para apoio à identificação de indicativo de diabetes a partir de dados clínicos tabulares. A análise exploratória permitiu compreender a estrutura da base, identificar inconsistências relevantes e definir uma estratégia de pré-processamento coerente com o problema.

Na etapa de modelagem, o modelo `RandomForest` apresentou o melhor equilíbrio entre desempenho global e capacidade de identificar corretamente casos positivos, superando a `LogisticRegression` nas métricas analisadas. A análise de interpretabilidade também se mostrou coerente com os achados exploratórios, especialmente no destaque de variáveis como `Glucose`, `BMI` e `Age`.

Em conjunto, os resultados indicam que a abordagem possui potencial como ferramenta de apoio à triagem, desde que respeitadas as limitações da base, a necessidade de validação adicional e o papel indispensável da supervisão profissional em contextos reais.
