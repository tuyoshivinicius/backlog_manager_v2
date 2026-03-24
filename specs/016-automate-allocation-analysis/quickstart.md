# Quickstart: EP-016 Automacao do Ciclo de Analise de Alocacao

**Date**: 2026-03-13

## Pre-requisitos

1. Python 3.11+ instalado
2. Poetry instalado (pip install poetry)
3. Dependencias do projeto instaladas (poetry install)
4. EP-014 (seed script) implementado
5. EP-015 (logging estruturado) implementado

## Uso Basico

### Execucao Completa

Invoque o skill para executar o ciclo completo de analise:

    /analyze-allocation

O skill executara automaticamente:
1. Seed script para gerar dados de teste
2. Testes de integracao de alocacao
3. Coleta e analise de logs
4. Identificacao de anomalias
5. Apresentacao de relatorio

### Analise de Logs Existentes

Para analisar logs de uma execucao anterior sem re-executar:

    /analyze-allocation --logs-only

## Formato do Relatorio

O skill apresenta um relatorio estruturado:

    ## Relatorio de Analise de Alocacao

    **Timestamp**: 2026-03-13T10:30:00
    **Modo**: full

    ### Metricas

    | Metrica | Valor |
    |---------|-------|
    | stories_allocated | 190 |
    | stories_processed | 190 |
    | waves_processed | 7 |
    | total_iterations | 350 |
    | deadlocks_detected | 0 |
    | ... | ... |

    ### Anomalias Identificadas

    Nenhuma anomalia detectada. OU

    CRITICAL: Deadlock detectado
    - Metrica: deadlocks_detected = 2
    - Threshold: > 0
    - Historias bloqueadas: CART-015, CART-016

## Fluxo de Correcao

Se uma anomalia for detectada:

1. Skill apresenta proposta de correcao
2. Usuario responde: aprovar / rejeitar / modificar
3. Se aprovado, skill aplica a correcao
4. Skill executa validacao automatica
5. Skill apresenta comparativo de metricas
6. Skill gera log de correcao

## Tabela de Correlacao Comportamento-Metrica

| Comportamento Observado | Metrica a Verificar | Acao Sugerida |
|-------------------------|---------------------|---------------|
| Historias nao alocadas | deadlocks_detected | Revisar dependencias |
| Distribuicao desbalanceada | skill_match_ratio | Ajustar criterio |
| Gaps no cronograma | max_idle_violations_detected | Ajustar max_idle_days |
| Datas atrasadas | date_adjustments | Revisar dependencias |

## Thresholds de Anomalia

| Metrica | Threshold | Severidade |
|---------|-----------|------------|
| deadlocks_detected | > 0 | CRITICAL |
| max_idle_violations_detected | > 5 | HIGH |
| max_idle_violations_detected | > 0 | MEDIUM |
| skill_match_ratio | < 0.5 | MEDIUM |

## Troubleshooting

### Skill nao encontra logs

Verificar localizacao:
- Windows: %APPDATA%/BacklogManager/logs/
- Linux: ~/.config/backlog_manager/logs/

### Seed script falha

1. Verificar poetry install foi executado
2. Verificar branch correto
3. Verificar permissoes de escrita no BD

### Correcao quebra testes

O skill detectara a falha e sugerira rollback. Nao persiste mudancas que falham na validacao.
