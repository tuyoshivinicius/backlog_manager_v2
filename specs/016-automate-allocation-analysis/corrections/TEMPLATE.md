# Log de Correcao: [ID]

**Timestamp**: [YYYY-MM-DDTHH:MM:SS]
**Branch**: 016-automate-allocation-analysis
**Feature**: EP-016 Automacao do Ciclo de Analise de Alocacao

## Problema Identificado

**Anomalia**: [CRITICAL/HIGH/MEDIUM] - [Tipo]
**Metrica**: [nome_metrica] = [valor_atual]
**Threshold**: [operador] [valor_esperado]
**Descricao**: [Descricao detalhada do problema observado]

## Diagnostico

**Causa Raiz**: [Analise da causa do problema]

**Arquivos Envolvidos**:
- [arquivo1.py]
- [arquivo2.py]

## Mudanca Aplicada

**Arquivos Modificados**:
- [arquivo1.py]: [descricao da mudanca]

**Codigo Alterado**:

    # Antes
    [codigo anterior]

    # Depois
    [codigo novo]

## Resultado

### Metricas Antes/Depois

| Metrica | Antes | Depois | Delta |
|---------|-------|--------|-------|
| stories_allocated | [X] | [Y] | [+/-Z] |
| deadlocks_detected | [X] | [Y] | [+/-Z] |
| max_idle_violations_detected | [X] | [Y] | [+/-Z] |
| ... | ... | ... | ... |

### Validacao

| Gate | Status | Valor |
|------|--------|-------|
| Testes | [PASS/FAIL] | [N] testes |
| Cobertura | [PASS/FAIL] | [X]% (>= 80%) |
| Complexidade | [PASS/FAIL] | CC [Y] (<= 15) |

## Conclusao

**Status Final**: [SUCESSO/FALHA/ROLLBACK]
**Proximos Passos**: [Se aplicavel]
