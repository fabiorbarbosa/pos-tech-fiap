# Relatório Técnico - Tech Challenge Fase 2

## Otimização de rotas médicas com algoritmo genético e suporte a LLM

**Pós-graduação:** IA para Devs  
**Instituição:** FIAP + Alura  
**Fase:** Fase 2  
**Desafio:** Tech Challenge  

**Integrante:**  
- Fábio Rodrigues Barbosa

**Data:** 14/07/2026

## Links da entrega

Os artefatos principais deste projeto podem ser acessados nos links abaixo:

- **Repositório Git:**
[https://github.com/fabiorbarbosa/pos-tech-fiap/tree/main/fase-02/tech-challenge](https://github.com/fabiorbarbosa/pos-tech-fiap/tree/main/fase-02/tech-challenge)
- **Vídeo de demonstração:**
[https://vimeo.com/XXXXXXXX](https://vimeo.com/XXXXXXXX)
<div style="page-break-after: always;"></div>

## 1. Introdução

Este projeto apresenta uma solução de otimização de rotas para distribuição simulada de medicamentos e insumos médicos em operação last-mile. A proposta foi desenvolvida no contexto do Tech Challenge da Fase 2 da pós-graduação IA para Devs, com foco no uso de algoritmos genéticos para gerar rotas mais eficientes e no uso de artefatos textuais para ampliar a interpretabilidade operacional da solução.

O problema foi tratado como uma adaptação do contexto logístico hospitalar descrito no enunciado. Como base de trabalho, foi utilizada uma massa real de entregas do Amazon Delivery Dataset, reinterpretada como cenário de distribuição médica. A partir dessa base, foi definido um recorte médico simplificado, com duas classes principais de entrega: `medicamentos_criticos` e `insumos_medicos`.

Além da otimização via algoritmo genético, a solução também contempla a geração de instruções operacionais, relatório gerencial e prompt-base para integração com uma LLM, aproximando a saída numérica do modelo de formatos mais interpretáveis para equipes humanas.

## 2. Definição do problema

O problema abordado consiste em encontrar rotas eficientes para uma frota de veículos responsável por realizar entregas médicas em ambiente urbano. Em termos práticos, a solução busca distribuir entregas entre diferentes veículos, minimizando custo total de rota e respeitando restrições operacionais como capacidade de carga, autonomia e prioridade das entregas.

Como o enunciado do projeto solicita um problema do tipo TSP/VRP com restrições realistas, o modelo foi estruturado como um problema de roteirização multi-veículo simplificado. Cada entrega foi tratada como uma parada com coordenadas geográficas, demanda e prioridade. A frota, por sua vez, foi composta por quatro tipos de veículo com limites de capacidade e distância máxima.

Do ponto de vista do uso prático, o objetivo não foi reproduzir uma operação hospitalar real com fidelidade clínica integral, mas construir uma simulação metodologicamente consistente de distribuição de medicamentos e insumos em cenário de última milha, suficiente para sustentar a comparação entre configurações do algoritmo genético e a produção dos artefatos exigidos pelo trabalho.

## 3. Base utilizada

O fluxo inicial do projeto foi estruturado com uma base sintética apenas para validação de código. Para a entrega principal, foi adotado o `Amazon Delivery Dataset`, que oferece volume suficiente de entregas e coordenadas para experimentos de roteirização com algoritmo genético.

A base bruta utilizada contém as seguintes colunas principais:

- `Order_ID`
- `Vehicle`
- `Store_Latitude`
- `Store_Longitude`
- `Drop_Latitude`
- `Drop_Longitude`
- `Category`
- `Traffic`
- `Weather`
- `Delivery_Time`

A base completa possuía `43.739` registros. Como nem todas as categorias do dataset bruto eram adequadas para a narrativa de distribuição médica, foi aplicado um mapeamento semântico para reinterpretar parte das categorias como entregas de saúde:

- `medicamentos_criticos`: categorias como `Skincare`, `Cosmetics` e `Grocery`
- `insumos_medicos`: categorias como `Home`, `Kitchen`, `Pet Supplies` e `Outdoors`

Categorias com aderência muito baixa ao contexto médico, como `Electronics`, `Books`, `Toys` e `Jewelry`, foram removidas do recorte principal. Após esse filtro, a base convertida passou a conter `18.935` entregas mais `1` depósito.

Em seguida, foi criada uma amostra reprodutível de `100` entregas para os experimentos dos notebooks, preservando a proporção entre `medicamentos_criticos` e `insumos_medicos`. Durante essa etapa também foram removidos pontos com coordenadas anômalas muito próximas de zero, que poderiam distorcer o cálculo das distâncias.

As regras de modelagem adotadas foram:

- `medicamentos_criticos`: demanda `2`, prioridade base `5`
- `insumos_medicos`: demanda `3`, prioridade base `4`
- `Traffic = jam`: incremento de `+1` na prioridade, limitado a `5`

Essa adaptação foi tratada explicitamente como uma camada de simulação sobre uma base logística real, e não como descrição literal da origem dos dados.

## 4. Modelagem genética

O algoritmo genético foi estruturado para operar sobre uma sequência de entregas, distribuindo-as entre os veículos disponíveis e avaliando cada solução por meio de uma função fitness penalizada. A representação cromossômica utilizada foi uma lista ordenada de identificadores de entrega, que posteriormente era particionada entre os veículos segundo os limites operacionais definidos.

Os principais componentes da modelagem foram:

- representação da solução como sequência de entregas;
- crossover por ordem;
- mutação por troca;
- elitismo;
- função fitness com distância, capacidade, autonomia e prioridade.

Na função fitness, a distância percorrida representa o custo principal da rota. Sobre esse custo foram adicionadas penalidades por excesso de carga, excesso de distância e atraso implícito de entregas de maior prioridade em posições tardias da sequência.

O fluxo geral de evolução foi:

1. gerar população inicial aleatória;
2. avaliar fitness de cada indivíduo;
3. ordenar população;
4. preservar elite;
5. selecionar pais por torneio;
6. aplicar crossover e mutação;
7. repetir por número fixo de gerações.

Essa formulação foi suficiente para comparar configurações do algoritmo dentro de um contexto de VRP simplificado, mantendo o código compacto e reproduzível.

## 5. Restrições consideradas

As restrições consideradas no experimento foram compatíveis com o escopo do trabalho e com a massa de teste selecionada.

Restrições incorporadas:

- capacidade máxima de carga por veículo;
- distância máxima por veículo;
- distribuição das entregas entre múltiplos veículos;
- prioridade de entrega refletida na função fitness;
- demanda diferenciada por classe de entrega.

Durante o Notebook 2, a frota inicial mostrou-se inviável para a amostra escolhida. A demanda total da amostra era `257`, enquanto a capacidade total da frota era apenas `58`. De forma análoga, a autonomia total da frota era `105`, enquanto a distância total encontrada no baseline inicial era `382.69`.

Por isso, foi realizada uma recalibração progressiva da frota até chegar a uma configuração experimental viável para comparação entre algoritmos:

- `motorcycle`: capacidade `65`, distância máxima `140`
- `van`: capacidade `85`, distância máxima `210`
- `scooter`: capacidade `65`, distância máxima `140`
- `bicycle`: capacidade `46`, distância máxima `120`

Essa decisão foi tratada como parte da modelagem do experimento, e não como ajuste arbitrário, pois o objetivo era avaliar o comportamento do algoritmo genético em uma instância operacionalmente viável sem reduzir demais a massa de teste.

## 6. Experimentos e resultados

Foram executados três experimentos principais com a mesma amostra de `100` entregas e a mesma frota recalibrada. Os parâmetros avaliados foram tamanho da população, número de gerações e taxa de mutação.

Configurações testadas:

- `exp_1_base`: população `80`, gerações `120`, mutação `0.15`
- `exp_2_more_generations`: população `80`, gerações `200`, mutação `0.15`
- `exp_3_more_population`: população `120`, gerações `120`, mutação `0.10`

Resultados consolidados:

| Experimento | Population Size | Generations | Mutation Rate | Best Fitness | Total Distance |
|---|---:|---:|---:|---:|---:|
| exp_3_more_population | 120 | 120 | 0.10 | 31403.70 | 583.70 |
| exp_2_more_generations | 80 | 200 | 0.15 | 31419.74 | 580.94 |
| exp_1_base | 80 | 120 | 0.15 | 31519.40 | 575.40 |

O menor fitness foi obtido em `exp_3_more_population`, indicando melhor desempenho global segundo a função objetivo adotada. Embora essa configuração não tenha apresentado a menor distância total entre os cenários comparados, a diferença observada sugere que o ganho da população maior sobre as penalidades operacionais compensou o pequeno aumento de distância.

Na etapa final de avaliação, a solução consolidada apresentou:

- `Best fitness`: `31519.0`
- `Total distance`: `605.7`

Distribuição final das rotas:

| Veículo | Num Stops | Distance | Load | Capacity Overflow | Distance Overflow |
|---|---:|---:|---:|---:|---:|
| motorcycle | 25 | 135.43 | 64 | 0 | 0.00 |
| van | 30 | 209.77 | 82 | 0 | 0.00 |
| scooter | 25 | 140.83 | 65 | 0 | 0.83 |
| bicycle | 20 | 119.67 | 46 | 0 | 0.00 |

O excesso residual de `0.83` em distância no veículo `scooter` foi tratado como desprezível para fins acadêmicos, dado o contexto de simulação e a comparabilidade preservada entre os experimentos.

Resultados automáticos gerados pelo fluxo final:

- `results/driver_instructions_final.md`
- `results/operations_report_final.md`
- `results/llm_prompt_final.txt`
- `figures/rotas-otimizadas-final-clean.png`
- `figures/convergencia-ga-final.png`

## 7. Integração com LLM

O projeto também incorporou uma camada textual de apoio operacional a partir da solução final. Para isso, foram gerados três artefatos:

- instruções operacionais para motoristas;
- relatório operacional de apoio gerencial;
- prompt-base para interação com uma LLM.

O arquivo `results/llm_prompt_final.txt` foi estruturado para fornecer a uma LLM o contexto mínimo necessário da operação:

- lista de veículos;
- distância total estimada;
- carga por rota;
- paradas por veículo;
- orientação para priorizar entregas mais urgentes na narrativa.

Os artefatos textuais gerados mostraram que a solução técnica pode ser traduzida para formatos mais interpretáveis por equipes humanas. As instruções para motoristas e o relatório operacional ficaram estruturalmente corretos e legíveis, embora ainda reflitam a camada de abstração adotada no mapeamento das categorias do dataset.

Mesmo assim, a integração foi considerada adequada ao escopo da fase, pois demonstra a capacidade de converter a saída do algoritmo genético em suporte textual de operação e de apresentação de resultados.

## 8. Discussão crítica

Os resultados mostram que foi possível construir uma solução coerente de roteirização multi-veículo com algoritmo genético a partir de uma base logística real adaptada ao contexto médico. A etapa de amostragem, limpeza e recalibração da frota foi decisiva para transformar a base em uma instância viável de experimento.

Ao mesmo tempo, o projeto possui limitações claras. A principal delas está na própria origem do dataset, que não foi criado para distribuição de medicamentos. O contexto médico foi obtido por reinterpretação controlada das categorias do Amazon Delivery Dataset, o que torna a narrativa metodologicamente defensável, mas não clinicamente literal.

Outra limitação está no nível de simplificação do modelo. O algoritmo não considera janelas de tempo explícitas, nem restrições de sequenciamento clínico mais avançadas. Além disso, a representação espacial trabalha apenas com coordenadas e distâncias aproximadas, sem incorporar malha viária real.

Por fim, a necessidade de recalibrar a frota mostra que a viabilidade operacional não estava dada pelos dados de entrada, e precisou ser modelada. Isso não invalida o experimento; ao contrário, evidencia a importância da etapa de diagnóstico da instância antes da comparação de configurações do algoritmo.

## 9. Conclusão

O projeto demonstrou que é possível estruturar uma solução de otimização de rotas médicas com algoritmo genético a partir de uma base real de entregas reinterpretada para fins de simulação acadêmica. A base foi limpa, filtrada, amostrada e adaptada para representar um cenário de distribuição de `medicamentos_criticos` e `insumos_medicos`.

Na etapa de modelagem, o algoritmo genético foi capaz de gerar soluções comparáveis entre diferentes configurações, destacando o efeito positivo do aumento do tamanho da população sobre o fitness final. A configuração `exp_3_more_population` foi selecionada como melhor referência entre os experimentos avaliados.

Além da otimização numérica, o projeto também produziu figuras, instruções operacionais, relatório gerencial e prompt-base para uso com LLM, ampliando a interpretabilidade da solução e aproximando-a das exigências do desafio.

Em conjunto, os resultados indicam que a abordagem proposta atende ao objetivo da Fase 2 ao combinar algoritmos genéticos, restrições operacionais e recursos iniciais de linguagem natural em uma entrega consistente, reproduzível e adequada ao escopo acadêmico do Tech Challenge.
