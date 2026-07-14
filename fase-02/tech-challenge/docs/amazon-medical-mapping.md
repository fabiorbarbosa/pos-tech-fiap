# Amazon Dataset -> Medical Delivery Mapping

## Objetivo

Este documento registra a lógica usada para adaptar o `Amazon Delivery Dataset` ao contexto do Projeto 2 do Tech Challenge, convertendo categorias de e-commerce em classes simuladas de entregas médicas.

## Premissa metodológica

O dataset original não contém categorias nativas de saúde. Por isso, a base foi tratada como uma simulação controlada de logística last-mile, e não como uma base hospitalar literal.

## Classes adotadas na entrega final

### `medicamentos_criticos`

Categorias mapeadas:

- `Skincare`
- `Cosmetics`
- `Grocery`

Regras aplicadas:

- demanda `2`
- prioridade base `5`

### `insumos_medicos`

Categorias mapeadas:

- `Home`
- `Kitchen`
- `Pet Supplies`
- `Outdoors`

Regras aplicadas:

- demanda `3`
- prioridade base `4`

## Categorias removidas

As categorias abaixo foram excluídas do recorte principal por baixa aderência à narrativa médica:

- `Electronics`
- `Books`
- `Jewelry`
- `Toys`
- `Apparel`
- `Shoes`
- `Sports`
- `Clothing`
- `Snacks`

## Regra adicional de prioridade

- `Traffic = jam` adiciona `+1` à prioridade, com limite máximo de `5`

## Frota final usada no experimento

- `motorcycle`: capacidade `65`, distância máxima `140`
- `van`: capacidade `85`, distância máxima `210`
- `scooter`: capacidade `65`, distância máxima `140`
- `bicycle`: capacidade `46`, distância máxima `120`

## Arquivos derivados

- `dataset/converted/stops_from_amazon.csv`
- `dataset/converted/vehicles_from_amazon.csv`
- `dataset/samples/stops_sample_100.csv`
- `dataset/samples/vehicles_sample_100.csv`
- `dataset/samples/vehicles_sample_100_experiment.csv`

## Observação

Esse mapeamento foi usado como baseline da entrega final e está alinhado ao relatório técnico, aos notebooks e ao `run_demo.py`.
