# Skill Contract: /analyze-allocation

**Date**: 2026-03-13

## Skill Definition

| Campo | Valor |
|-------|-------|
| Name | analyze-allocation |
| Location | .claude/commands/analyze-allocation.md |
| Description | Automatizar ciclo de analise de alocacao |

## Interface

### Invocation

- /analyze-allocation - Execucao completa (seed + testes + analise)
- /analyze-allocation --logs-only - Analise de logs existentes

### Inputs

| Parametro | Tipo | Default | Descricao |
|-----------|------|---------|-----------|
| --logs-only | flag | false | Analisar logs existentes sem re-execucao |

### Outputs

1. **Relatorio de Analise** (sempre gerado):
   - Timestamp da analise
   - Modo de execucao (full/logs-only)
   - Tabela com 16 metricas
   - Lista de anomalias identificadas
   - Recomendacoes de acao

2. **Proposta de Correcao** (se anomalia detectada):
   - Arquivos a modificar
   - Mudancas propostas
   - Impacto esperado nas metricas
   - Codigo proposto (quando aplicavel)

3. **Resultado de Validacao** (apos correcao aprovada):
   - Status dos testes
   - Cobertura de codigo
   - Complexidade ciclomatica
   - Tabela comparativa de metricas (antes/depois)

4. **Log de Correcao** (apos validacao bem-sucedida):
   - Arquivo CORRECAO-{timestamp}.md criado em corrections/

## Behavior Contract

### Preconditions

| ID | Condicao | Acao se Falhar |
|----|----------|----------------|
| PRE-001 | Poetry instalado | Halt com mensagem de instalacao |
| PRE-002 | Dependencias instaladas | Sugerir poetry install |
| PRE-003 | Branch correto (se --logs-only=false) | Halt com aviso |
| PRE-004 | Logs existem (se --logs-only=true) | Halt com mensagem informativa |

### Postconditions

| ID | Condicao | Verificacao |
|----|----------|-------------|
| POST-001 | Relatorio gerado com 16 metricas | Todas metricas presentes |
| POST-002 | Anomalias priorizadas | CRITICAL antes de HIGH antes de MEDIUM |
| POST-003 | Codigo nao modificado sem aprovacao | Aguardar input do usuario |
| POST-004 | Validacao executada apos correcao | Testes + cobertura + CC |

### Error Handling

| Cenario | Comportamento |
|---------|---------------|
| Seed script falha | Halt, mostrar erro, sugerir verificar pre-requisitos |
| Log parsing falha | Halt, reportar parsing failure, sugerir verificar logging |
| Correcao quebra testes | Detectar falha, sugerir rollback, nao persistir |
| Usuario cancela | Nao persistir estado parcial, proxima invocacao limpa |
| Multiplas anomalias | Priorizar por severidade, uma por vez |

**IMPORTANTE**: Skill NAO faz retry automatico em caso de falha.

## Execution Flow

### Full Mode (default)

1. Verificar pre-requisitos (poetry, dependencias)
2. Executar: poetry run python scripts/seed_test_backlog.py --clean
3. Executar: poetry run pytest tests/integration/ -k allocation -v
4. Localizar log mais recente em logs directory
5. Extrair 16 metricas do log
6. Identificar anomalias baseado em thresholds
7. Apresentar relatorio estruturado
8. Se anomalia, gerar proposta de correcao
9. Aguardar aprovacao do usuario
10. Se aprovado, aplicar correcao
11. Executar validacao (testes + cobertura + CC)
12. Re-executar seed + testes para comparar metricas
13. Apresentar tabela comparativa
14. Gerar log de correcao

### Logs-Only Mode (--logs-only)

1. Verificar pre-requisitos
2. Localizar log mais recente
3. Se nao encontrado, halt com mensagem informativa
4. Extrair 16 metricas do log
5. Identificar anomalias
6. Apresentar relatorio
7. (Continua igual ao full mode a partir de proposta de correcao)

## Thresholds

| Metrica | Threshold | Severidade |
|---------|-----------|------------|
| deadlocks_detected | > 0 | CRITICAL |
| max_idle_violations_detected | > 5 | HIGH |
| max_idle_violations_detected | > 0 | MEDIUM |
| skill_match_ratio | < 0.5 | MEDIUM |

Onde skill_match_ratio = allocations_by_dependency_owner / (allocations_by_dependency_owner + allocations_by_load_balancing)
