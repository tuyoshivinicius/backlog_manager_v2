# Data Model: EP-016 Automacao do Ciclo de Analise de Alocacao

**Date**: 2026-03-13

## Overview

Este EP nao introduz novas entidades persistentes no dominio. O skill opera sobre entidades existentes (AllocationMetrics, Story, Developer, Feature) e gera artefatos de documentacao (relatorios, logs de correcao).

## Entities (Reusadas)

### AllocationMetrics (domain/services/allocation_service.py)

Dataclass existente que captura todas as 16 metricas de alocacao:

| Campo | Tipo | Descricao |
|-------|------|-----------|
| total_time_seconds | float | Tempo total de execucao |
| stories_processed | int | Total de historias processadas |
| stories_allocated | int | Historias alocadas com sucesso |
| waves_processed | int | Numero de ondas processadas |
| total_iterations | int | Total de iteracoes do algoritmo |
| iterations_per_wave | dict[int, int] | Iteracoes por onda |
| allocations_by_dependency_owner | int | Alocacoes por DEPENDENCY_OWNER |
| allocations_by_load_balancing | int | Alocacoes por LOAD_BALANCING |
| deadlocks_detected | int | Deadlocks detectados |
| date_adjustments | int | Ajustes de data realizados |
| validation_reallocations | int | Realocacoes na validacao |
| validation_dependency_fixes | int | Dependencias corrigidas |
| validation_conflict_fixes | int | Conflitos resolvidos |
| max_idle_violations_detected | int | Violacoes de max_idle detectadas |
| max_idle_violations_fixed | int | Violacoes corrigidas |
| failed_reallocations | int | Realocacoes falhas |

## Conceptual Entities (Skill-Only)

Estas entidades existem apenas como conceitos no fluxo do skill, nao como classes Python:

### AllocationAnalysisReport (Conceitual)

Relatorio gerado pela analise, formatado em markdown:

| Campo | Tipo | Descricao |
|-------|------|-----------|
| timestamp | datetime | Momento da analise |
| execution_mode | string | full ou logs-only |
| metrics | AllocationMetrics | Metricas extraidas |
| anomalies | list[Anomaly] | Anomalias identificadas |
| recommendations | list[string] | Recomendacoes de acao |

### Anomaly (Conceitual)

Anomalia identificada na analise:

| Campo | Tipo | Descricao |
|-------|------|-----------|
| severity | CRITICAL/HIGH/MEDIUM | Nivel de severidade |
| type | string | Tipo da anomalia (deadlock/idle/skill_match) |
| metric_name | string | Nome da metrica afetada |
| actual_value | number | Valor atual |
| threshold | number | Threshold esperado |
| description | string | Descricao do problema |

### CorrectionProposal (Conceitual)

Proposta de correcao formatada:

| Campo | Tipo | Descricao |
|-------|------|-----------|
| anomaly | Anomaly | Anomalia sendo corrigida |
| target_files | list[string] | Arquivos a modificar |
| proposed_changes | list[string] | Mudancas propostas |
| expected_impact | dict[string, string] | Impacto esperado nas metricas |
| code_diff | string | Diff do codigo proposto (opcional) |

### ValidationResult (Conceitual)

Resultado da validacao pos-correcao:

| Campo | Tipo | Descricao |
|-------|------|-----------|
| tests_passed | bool | Todos os testes passaram |
| test_count | int | Numero de testes executados |
| coverage_percent | float | Cobertura de codigo |
| coverage_passed | bool | Cobertura >= 80 porcento |
| cyclomatic_complexity | float | Complexidade ciclomatica media |
| complexity_passed | bool | CC <= 15 |
| metrics_before | AllocationMetrics | Metricas antes da correcao |
| metrics_after | AllocationMetrics | Metricas depois da correcao |
| metrics_delta | dict[string, number] | Diferenca entre metricas |

## File Artifacts

### Correction Log Template

Arquivo: specs/016-automate-allocation-analysis/corrections/TEMPLATE.md

Template para documentar correcoes aplicadas:

| Secao | Conteudo |
|-------|----------|
| Cabecalho | ID, timestamp, branch |
| Problema | Descricao da anomalia |
| Diagnostico | Analise da causa raiz |
| Mudanca | Arquivos modificados, diff |
| Resultado | Metricas antes/depois, delta |
| Validacao | Status dos testes, cobertura, CC |

### Log Files

Localizacao:
- Windows: %APPDATA%/BacklogManager/logs/backlog_manager.log
- Linux: ~/.config/backlog_manager/logs/backlog_manager.log

Formato: timestamp - LEVEL - name - message

## Relationships

Nao ha novos relacionamentos entre entidades. O skill apenas le dados existentes e gera artefatos de documentacao.

## State Transitions

O skill nao modifica estados de entidades de dominio. Apenas:
1. Executa comandos que podem criar/modificar dados (seed script)
2. Le logs e extrai metricas (read-only)
3. Gera relatorios em formato texto (output)
4. Aplica correcoes de codigo (com aprovacao)
