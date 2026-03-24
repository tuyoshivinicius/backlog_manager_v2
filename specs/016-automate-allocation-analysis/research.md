# Research: EP-016 Automacao do Ciclo de Analise de Alocacao

**Date**: 2026-03-13

## Research Tasks

### R1: Claude Code Skill Structure and Best Practices

**Context**: Este EP implementa um Claude Code Skill para automatizar o ciclo de analise de alocacao.

**Findings**:

1. **Estrutura de Skills Claude Code**:
   - Skills sao arquivos markdown em .claude/commands/
   - Frontmatter YAML com description (obrigatorio) e allowed-tools (opcional)
   - Corpo do skill contem instrucoes em markdown para o Claude executar
   - Skills podem usar ARGUMENTS para receber parametros do usuario

2. **Melhores Praticas**:
   - Skills devem ter um fluxo claro com etapas numeradas
   - Cada etapa deve ter criterios de sucesso/falha claros
   - Evitar loops infinitos com limites explicitos
   - Usar ferramentas nativas (Bash, Read, Write, Edit) quando possivel
   - Skill NAO deve fazer retry automatico em caso de falha

3. **Padrao de Erro Observado**:
   - Skills existentes (speckit.*) usam padrao de halt + mensagem clara
   - Nunca tentam retry automatico
   - Sugerem proximos passos manualmente

**Decision**: O skill /analyze-allocation seguira o mesmo padrao dos skills speckit, com etapas numeradas claras, halt em caso de erro com mensagem acionavel, e sem retry automatico.

**Rationale**: Consistencia com skills existentes no projeto; alinhamento com requisito FR do spec.

**Alternatives Considered**: Script Python para automacao (rejeitado - complexidade desnecessaria), Hook de pre-commit (rejeitado - analise deve ser manual)

---

### R2: Log Parsing and AllocationMetrics Extraction

**Context**: O skill deve extrair as 16 metricas de AllocationMetrics dos logs estruturados (EP-015).

**Findings**:

1. **Formato de Log Atual**: timestamp - LEVEL - name - message
2. **Logs Estruturados do AllocationService**: Log INFO final com metricas principais, Log DEBUG com metricas detalhadas, Logs WARNING para deadlocks e ociosidade
3. **As 16 Metricas**: total_time_seconds, stories_processed, stories_allocated, waves_processed, total_iterations, iterations_per_wave, allocations_by_dependency_owner, allocations_by_load_balancing, deadlocks_detected, date_adjustments, validation_reallocations, validation_dependency_fixes, validation_conflict_fixes, max_idle_violations_detected, max_idle_violations_fixed, failed_reallocations

**Decision**: O skill usara combinacao de grep + instrucoes de parsing inline. O Claude interpretara os logs diretamente.

**Rationale**: Simplicidade; evita adicionar codigo Python; aproveita capacidade do Claude de interpretar texto estruturado.

**Alternatives Considered**: Script Python para parsing (rejeitado - complexidade), JSON structured logging (rejeitado - mudaria formato EP-015)

---

### R3: Anomaly Detection Thresholds

**Context**: O skill deve identificar anomalias baseado em thresholds definidos (FR-006).

**Findings**:

1. **Thresholds do Spec**: deadlocks > 0, idle_violations > 0, skill_match_ratio < 0.5
2. **Correlacao Comportamento-Metrica**: Distribuicao desbalanceada -> skill_match_ratio; Historias bloqueadas -> deadlocks_detected; Gaps cronograma -> max_idle_violations_detected
3. **Severidade**: CRITICAL (deadlocks > 0), HIGH (idle_violations > 5), MEDIUM (skill_match_ratio < 0.5, idle_violations > 0)

**Decision**: Implementar deteccao com tres niveis (CRITICAL/HIGH/MEDIUM). Reportar uma anomalia por vez para correcao incremental.

**Rationale**: Alinhamento com spec; priorizacao clara para o usuario.

**Alternatives Considered**: Reportar todas anomalias (rejeitado - spec define correcao incremental)

---

### R4: Correction Proposal Generation

**Context**: O skill deve gerar propostas de correcao com codigo especifico e arquivos alvo (FR-009).

**Findings**:

1. **Anomalias Conhecidas e Correcoes**: Deadlock -> revisar dependencias; Idle violations -> ajustar max_idle_days; Low skill_match -> revisar criterio de alocacao
2. **Formato de Proposta**: Arquivos a modificar, mudancas propostas, impacto esperado nas metricas
3. **Fluxo de Aprovacao**: Apresentar proposta, aguardar resposta (aprovar/rejeitar/modificar), aplicar somente apos aprovacao

**Decision**: Usar formato padrao do quickstart EP-015 para propostas. Incluir codigo proposto inline com diff-style.

**Rationale**: Consistencia com documentacao existente; clareza para o usuario.

**Alternatives Considered**: Gerar PR automaticamente (rejeitado - requer aprovacao manual)

---

### R5: Validation Post-Correction

**Context**: O skill deve executar validacao completa apos cada correcao (FR-012 a FR-016).

**Findings**:

1. **Comandos de Validacao**: poetry run pytest (testes), cobertura >= 80 porcento, poetry run radon cc (CC <= 15), poetry run mypy (tipos)
2. **Comparativo de Metricas**: Re-executar seed + testes, extrair metricas novamente, calcular deltas, apresentar tabela
3. **Rollback**: Se validacao falha, sugerir rollback (nao automatico)

**Decision**: Validacao sequencial: testes -> cobertura -> complexidade -> metricas. Halt se qualquer gate falha.

**Rationale**: Ordem garante codigo funcional antes de metricas.

**Alternatives Considered**: Rollback automatico (rejeitado - usuario deve decidir)

---

## Summary of Decisions

| Area | Decision | Key Rationale |
|------|----------|---------------|
| Skill Structure | Seguir padrao speckit.* | Consistencia |
| Log Parsing | Grep + interpretacao Claude | Simplicidade |
| Anomaly Detection | 3 niveis (CRITICAL/HIGH/MEDIUM) | Priorizacao clara |
| Correction Proposals | Formato padrao EP-015 | Consistencia |
| Validation | Sequencial: tests -> coverage -> cc | Gates obrigatorios |
