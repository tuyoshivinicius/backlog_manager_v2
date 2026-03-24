# Feature Specification: Automacao do Ciclo de Analise de Alocacao

**Feature Branch**: `016-automate-allocation-analysis`
**Created**: 2026-03-12
**Status**: Draft
**Input**: User description: "EP-016: Automatizar o processo de análise de alocação - permitir que Claude Code execute seed script, rode alocação, analise logs, identifique problemas e proponha correções automaticamente, sem intervenção manual do usuário nas etapas de observação e análise"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Execucao Automatizada do Ciclo de Analise (Priority: P1)

O usuario invoca um skill do Claude Code (ex: `/analyze-allocation`) e o Claude Code automaticamente executa o ciclo completo: gera dados de teste via seed script, executa a alocacao, coleta os logs estruturados, analisa as metricas e apresenta um relatorio com problemas identificados e sugestoes de correcao.

**Why this priority**: Esta e a funcionalidade core que elimina a necessidade de o usuario executar manualmente cada etapa do protocolo de 6 passos. Automatiza as etapas 1-4 (Observar, Descrever, Analisar logs, Diagnosticar).

**Independent Test**: Pode ser testado invocando o skill e verificando que o relatorio final contem metricas extraidas dos logs e identificacao de problemas (se houver).

**Acceptance Scenarios**:

1. **Given** ambiente configurado com poetry e seed script EP-014, **When** usuario invoca `/analyze-allocation`, **Then** Claude Code executa `poetry run python scripts/seed_test_backlog.py --clean`, roda testes de alocacao, coleta logs e apresenta relatorio estruturado
2. **Given** alocacao completada com logs disponiveis, **When** Claude Code analisa metricas, **Then** relatorio inclui todas as 16 metricas de AllocationMetrics com interpretacao (valores normais vs anomalos)
3. **Given** logs indicam distribuicao desbalanceada (skill_match_ratio < 0.5 onde skill_match_ratio = allocations_by_dependency_owner / (allocations_by_dependency_owner + allocations_by_load_balancing)), **When** Claude Code identifica anomalia, **Then** relatorio inclui problema especifico com descricao e recomendacao de investigacao

---

### User Story 2 - Analise de Logs Existentes Sem Re-execucao (Priority: P2)

O usuario ja executou a alocacao previamente e quer que o Claude Code analise os logs existentes sem re-executar o seed script ou testes. O usuario invoca `/analyze-allocation --logs-only` e o Claude Code localiza os logs mais recentes, analisa e apresenta relatorio.

**Why this priority**: Permite analise rapida de execucoes anteriores sem custo de re-execucao, util para investigacoes incrementais.

**Independent Test**: Pode ser testado tendo logs pre-existentes e invocando com flag `--logs-only`, verificando que relatorio e gerado sem executar seed script.

**Acceptance Scenarios**:

1. **Given** logs de alocacao existem em %APPDATA%/BacklogManager/logs/, **When** usuario invoca `/analyze-allocation --logs-only`, **Then** Claude Code lê logs sem executar seed script ou testes
2. **Given** multiplos arquivos de log existem (rotacao), **When** Claude Code analisa, **Then** utiliza o arquivo mais recente por padrao
3. **Given** nenhum log de alocacao encontrado, **When** Claude Code tenta analisar, **Then** retorna mensagem informativa sugerindo executar alocacao primeiro

---

### User Story 3 - Proposta Automatica de Correcao com Pre-aprovacao (Priority: P2)

Apos identificar um problema na alocacao, o Claude Code automaticamente propoe uma correcao com codigo especifico, lista de arquivos a modificar e impacto esperado. A correcao so e aplicada apos aprovacao explicita do usuario.

**Why this priority**: Automatiza a etapa 5 (Propor correcao) mantendo o usuario no controle da decisao final. Garante que correcoes nao sao aplicadas sem consentimento.

**Independent Test**: Pode ser testado identificando um problema conhecido (ex: via mock de logs) e verificando que proposta de correcao e formatada corretamente com codigo e impacto.

**Acceptance Scenarios**:

1. **Given** problema identificado (ex: deadlocks_detected > 0), **When** Claude Code gera proposta, **Then** proposta inclui: descricao do problema, arquivos a modificar, codigo proposto, impacto esperado nas metricas
2. **Given** proposta de correcao apresentada, **When** usuario responde "aprovar", **Then** Claude Code aplica a correcao e executa validacao (testes + metricas)
3. **Given** proposta de correcao apresentada, **When** usuario responde "rejeitar" ou modifica, **Then** Claude Code ajusta proposta ou abandona sem modificar codigo

---

### User Story 4 - Validacao Pos-Correcao Automatizada (Priority: P3)

Apos aplicar uma correcao, o Claude Code automaticamente executa a suite de testes, verifica cobertura >= 80%, verifica complexidade ciclomatica <= 15, e re-executa a alocacao para comparar metricas antes/depois.

**Why this priority**: Automatiza a etapa 6 (Validar) garantindo que correcoes nao introduzem regressoes.

**Independent Test**: Pode ser testado aplicando uma correcao mock e verificando que suite de testes e executada e metricas comparadas.

**Acceptance Scenarios**:

1. **Given** correcao aplicada, **When** Claude Code executa validacao, **Then** roda `poetry run pytest tests/ -v --cov=src/backlog_manager` e verifica exit code 0
2. **Given** validacao de testes concluida, **When** cobertura < 80% ou complexidade > 15, **Then** Claude Code alerta problema e sugere rollback ou ajuste
3. **Given** testes passam e metricas de qualidade ok, **When** Claude Code compara metricas de alocacao, **Then** apresenta tabela comparativa antes/depois com deltas

---

### User Story 5 - Documentacao Automatica de Correcao (Priority: P3)

Ao concluir um ciclo de correcao validado, o Claude Code automaticamente preenche o template de Log de Correcao (corrections/TEMPLATE.md) com todos os dados coletados durante o ciclo.

**Why this priority**: Automatiza a documentacao que seria feita manualmente, garantindo rastreabilidade completa.

**Independent Test**: Pode ser testado completando um ciclo de correcao e verificando que arquivo corrections/CORRECAOxxx.md e criado com campos preenchidos.

**Acceptance Scenarios**:

1. **Given** ciclo de correcao concluido com sucesso, **When** Claude Code documenta, **Then** cria arquivo specs/015-.../corrections/CORRECAO-{timestamp}.md com todos os campos do template preenchidos
2. **Given** metricas antes/depois disponiveis, **When** Claude Code preenche Log de Correcao, **Then** tabela de metricas inclui valores exatos e deltas calculados
3. **Given** documentacao criada, **When** usuario revisa, **Then** encontra todos os campos obrigatorios preenchidos (problema, diagnostico, mudanca, resultado)

---

### Edge Cases

- O que acontece quando seed script falha (dependencia faltando, erro de BD)?
  - Claude Code captura erro, apresenta mensagem e sugere verificar pre-requisitos
- O que acontece quando logs estao em formato inesperado ou corrompidos?
  - Claude Code reporta parsing failure e sugere verificar configuracao de logging
- O que acontece quando correcao proposta quebra testes existentes?
  - Claude Code detecta falha na validacao, reverte automaticamente e reporta que correcao nao e viavel
- O que acontece quando usuario cancela no meio do ciclo?
  - Estado parcial nao e persistido; proxima invocacao inicia ciclo limpo
- O que acontece quando multiplas anomalias sao detectadas?
  - Claude Code prioriza por severidade e apresenta uma por vez para correcao incremental
- O que acontece quando qualquer etapa automatizada falha?
  - Claude Code NAO faz retry automatico; falha imediatamente com mensagem de erro acionavel e proximos passos sugeridos

## Requirements *(mandatory)*

### Functional Requirements

**Execucao Automatizada:**

- **FR-001**: Sistema DEVE executar `poetry run python scripts/seed_test_backlog.py --clean` quando invocado sem flag `--logs-only`
- **FR-002**: Sistema DEVE executar `poetry run pytest tests/integration/ -k "allocation" -v` para gerar dados de alocacao
- **FR-003**: Sistema DEVE localizar e ler logs de alocacao em `%APPDATA%/BacklogManager/logs/` (Windows) ou `~/.config/backlog_manager/logs/` (Linux)
- **FR-004**: Sistema DEVE suportar flag `--logs-only` para analisar logs existentes sem re-execucao

**Analise de Metricas:**

- **FR-005**: Sistema DEVE extrair todas as 16 metricas de AllocationMetrics dos logs estruturados
- **FR-006**: Sistema DEVE identificar anomalias baseado em thresholds definidos (deadlocks > 0, idle_violations > 0, skill_match_ratio < 0.5 onde skill_match_ratio = allocations_by_dependency_owner / (allocations_by_dependency_owner + allocations_by_load_balancing))
- **FR-007**: Sistema DEVE correlacionar metricas com comportamentos visiveis (tabela de correlacao do quickstart EP-015)
- **FR-008**: Sistema DEVE apresentar relatorio estruturado com metricas, anomalias e recomendacoes

**Proposta de Correcao:**

- **FR-009**: Sistema DEVE gerar proposta de correcao com: descricao do problema, arquivos a modificar, codigo proposto, impacto esperado
- **FR-010**: Sistema DEVE aguardar aprovacao explicita do usuario antes de aplicar qualquer modificacao de codigo
- **FR-011**: Sistema DEVE permitir que usuario modifique proposta antes de aprovar

**Validacao:**

- **FR-012**: Sistema DEVE executar suite de testes completa apos cada correcao aplicada
- **FR-013**: Sistema DEVE verificar cobertura >= 80% (SC-006 do EP-015)
- **FR-014**: Sistema DEVE verificar complexidade ciclomatica <= 15 (SC-007 do EP-015)
- **FR-015**: Sistema DEVE comparar metricas de alocacao antes/depois da correcao
- **FR-016**: Sistema DEVE sugerir rollback se validacao falhar

**Documentacao:**

- **FR-017**: Sistema DEVE criar Log de Correcao automaticamente ao concluir ciclo com sucesso
- **FR-018**: Sistema DEVE preencher todos os campos obrigatorios do template de correcao

### Key Entities *(include if feature involves data)*

- **AllocationAnalysisReport**: Relatorio gerado pela analise contendo: timestamp, metricas extraidas (AllocationMetrics), anomalias identificadas, recomendacoes
- **CorrectionProposal**: Proposta de correcao contendo: problema identificado, arquivos alvo, codigo proposto, impacto esperado nas metricas
- **ValidationResult**: Resultado da validacao pos-correcao contendo: status dos testes, cobertura, complexidade ciclomatica, comparativo de metricas

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Usuario consegue executar ciclo completo de analise (etapas 1-4) com um unico comando em menos de 2 minutos (baseline: dados EP-014 seed com 190 historias, 7 ondas, 7 desenvolvedores)
- **SC-002**: 100% das 16 metricas de AllocationMetrics sao extraidas e apresentadas no relatorio
- **SC-003**: Anomalias conhecidas (deadlocks > 0, idle_violations > 0, skill_match_ratio < 0.5) sao identificadas em 100% dos casos
- **SC-004**: Propostas de correcao incluem codigo especifico e arquivos alvo em 100% dos casos
- **SC-005**: Validacao pos-correcao detecta 100% das regressoes (testes falhando)
- **SC-006**: Log de Correcao e gerado automaticamente com 100% dos campos obrigatorios preenchidos
- **SC-007**: Tempo total do ciclo completo (analise + correcao + validacao + documentacao) < 10 minutos para correcoes simples (definicao: modificacao de ate 3 arquivos com menos de 50 linhas alteradas no total)

## Assumptions

- EP-015 (logging estruturado) esta implementado e funcional
- EP-014 (seed script) esta implementado e funcional
- Ambiente tem poetry instalado e dependencias do projeto configuradas
- Logs seguem formato definido em contracts/logging-contract.md do EP-015
- Usuario tem permissoes para ler/escrever arquivos no projeto
- Claude Code tem acesso a ferramentas Bash, Read, Write, Edit

## Clarifications

### Session 2026-03-12

- Q: What constitutes a "desbalanced" allocation ratio that should trigger an anomaly? → A: Single threshold: skill_match_ratio < 0.5 onde skill_match_ratio = allocations_by_dependency_owner / (allocations_by_dependency_owner + allocations_by_load_balancing) (less than half allocated by skill match = desbalanced)
- Q: Should Claude Code retry automatically when an automated step fails? → A: No auto-retry; fail immediately with actionable error message

## Out of Scope

- Criacao de novos algoritmos de alocacao
- Modificacoes na GUI
- Exposicao de metricas via API externa
- Machine learning para predicao de problemas
- Integracao com sistemas de CI/CD externos
- Analise de performance em tempo real (apenas pos-execucao)
