# Feature Specification: Resolver Issues SonarQube e Aprovar Quality Gate

**Feature Branch**: `034-sonarqube-quality-gate`
**Created**: 2026-04-01
**Status**: Draft
**Input**: User description: "Resolver issues SonarQube e aprovar Quality Gate - refatorar complexidade cognitiva, revisar security hotspots, corrigir code smells"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Reduzir Complexidade Cognitiva de Funções Críticas (Priority: P1)

Como mantenedor do projeto, preciso que funções com complexidade cognitiva acima do limite permitido (15) sejam refatoradas em sub-funções menores e mais focadas, para que o código seja mais legível, testável e fácil de manter.

Há 6 funções identificadas com complexidade excessiva:
- `allocation_service.py` linha 1071 (complexidade 22, permitida 15)
- `extract_metrics.py` linha 254 (complexidade 19, permitida 15)
- `extract_metrics.py` linha 557 (complexidade 17, permitida 15)
- `seed_test_backlog.py` linha 600 (complexidade 19, permitida 15)
- `seed_test_backlog.py` linha 563 (complexidade 16, permitida 15)
- `story_table_model.py` linha 230 (complexidade 16, permitida 15)

**Why this priority**: Issues CRITICAL bloqueiam diretamente a aprovação do Quality Gate e indicam funções difíceis de manter e testar. A refatoração melhora a manutenibilidade do código de produção.

**Independent Test**: Pode ser validado executando a suíte de testes existente após cada refatoração e verificando no SonarQube que a complexidade cognitiva de cada função está ≤15.

**Acceptance Scenarios**:

1. **Given** uma função com complexidade cognitiva >15, **When** a função é refatorada em sub-funções auxiliares, **Then** a complexidade cognitiva da função principal é ≤15
2. **Given** uma função refatorada, **When** a suíte de testes existente é executada, **Then** todos os testes passam sem regressão
3. **Given** todas as 6 funções refatoradas, **When** o SonarQube analisa o código, **Then** nenhuma issue CRITICAL de complexidade cognitiva (S3776) permanece aberta

---

### User Story 2 - Revisar Security Hotspots para Aprovar Quality Gate (Priority: P1)

Como mantenedor do projeto, preciso que todos os 32 security hotspots pendentes de revisão sejam analisados e marcados com a resolução apropriada (SAFE, FIXED ou ACKNOWLEDGED), para que o critério de "Security Hotspots Reviewed = 100%" do Quality Gate seja satisfeito.

Os hotspots se dividem em:
- **9 MEDIUM**: 1 Regex DoS em teste, 1 permissão de workflow, 7 pseudo-random em script de seed
- **23 LOW**: 6 SHA de commit em GitHub Actions, 17 diretórios públicos em testes

**Why this priority**: O Quality Gate está falhando exclusivamente porque 0% dos security hotspots foram revisados (threshold: 100%). Este é o bloqueador direto da aprovação.

**Independent Test**: Pode ser validado verificando no SonarQube que o percentual de security hotspots revisados é 100% e o Quality Gate muda de ERROR para OK.

**Acceptance Scenarios**:

1. **Given** hotspots de pseudo-random em `seed_test_backlog.py` (contexto de seed/teste), **When** revisados, **Then** são marcados como SAFE pois o uso de `random` é intencional em dados de teste
2. **Given** hotspots de Regex DoS em arquivo de teste, **When** revisado, **Then** é marcado como SAFE pois o input é controlado em contexto de teste
3. **Given** hotspots de diretórios públicos em testes usando `tmp_path`, **When** revisados, **Then** são marcados como SAFE pois `tmp_path` do pytest gera diretórios temporários seguros
4. **Given** hotspots de SHA de commit em GitHub Actions, **When** as dependências são atualizadas para usar SHA completo, **Then** os hotspots são resolvidos como FIXED
5. **Given** hotspot de permissão de workflow em `publish.yml`, **When** revisado e corrigido especificando apenas os secrets necessários, **Then** o hotspot é resolvido como FIXED ou ACKNOWLEDGED
6. **Given** todos os 32 hotspots revisados, **When** o SonarQube reavalia, **Then** Security Hotspots Reviewed = 100%

---

### User Story 3 - Corrigir Code Smells (MAJOR e MINOR) (Priority: P2)

Como mantenedor do projeto, preciso que os code smells restantes sejam resolvidos para manter o código limpo e evitar acúmulo de dívida técnica.

Os code smells incluem:
- 1 MAJOR: código comentado em arquivo de teste (S125)
- 1 MINOR: bloco `except` vazio sem lógica (S2737)
- 1 MINOR: keyword `async` desnecessária em teste (S7503)
- 11 MINOR: naming conventions em mocks Qt — camelCase intencional (S100, S116)

**Why this priority**: Embora não bloqueiem o Quality Gate diretamente, code smells afetam a manutenibilidade e a nota geral do projeto. Os naming conventions dos mocks Qt requerem supressão, não renomeação.

**Independent Test**: Pode ser validado verificando no SonarQube que o total de issues OPEN diminui para zero.

**Acceptance Scenarios**:

1. **Given** código comentado em `test_schema.py` linha 86, **When** o bloco é removido, **Then** a issue S125 é resolvida
2. **Given** bloco `except` vazio em `main_window.py` linha 1408, **When** logging ou tratamento adequado é adicionado, **Then** a issue S2737 é resolvida
3. **Given** função `async` sem `await` em `test_scheduling_use_cases.py` linha 34, **When** o `async` é removido ou o `await` faltante é adicionado, **Then** a issue S7503 é resolvida
4. **Given** métodos camelCase em `headless_mocks.py` que mimetizam a API Qt, **When** exclusão do arquivo das regras S100/S116 é configurada no `sonar-project.properties`, **Then** as 11 issues de naming convention são resolvidas sem alterar os nomes dos métodos

---

### Edge Cases

- O que acontece se a refatoração de complexidade cognitiva quebrar testes existentes? Cada refatoração deve ser seguida de execução da suíte de testes completa antes de prosseguir.
- O que acontece se um security hotspot marcado como SAFE for reclassificado pelo SonarQube em análises futuras? A decisão de revisão persiste no SonarQube e não é reaberta automaticamente.
- O que acontece se a substituição de tags por SHA em GitHub Actions causar falha no CI? As versões de SHA devem ser verificadas contra as releases oficiais de cada action antes da substituição.
- O que acontece se a exclusão no `sonar-project.properties` não resolver as issues no SonarQube? Configurar exclusão adicional a nível de projeto diretamente na interface do SonarQube (Administration > General Settings > Analysis Scope) para o arquivo `tests/headless_mocks.py` nas regras S100 e S116.

## Clarifications

### Session 2026-04-01

- Q: Qual mecanismo de supressão para naming conventions (S100/S116) dos mocks Qt? → A: Exclusão do arquivo `tests/headless_mocks.py` das regras S100/S116 no `sonar-project.properties`

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Cada função com complexidade cognitiva >15 DEVE ser refatorada para atingir complexidade ≤15, mantendo o comportamento original
- **FR-002**: A refatoração DEVE extrair blocos lógicos para sub-funções auxiliares privadas, sem alterar a interface pública das funções
- **FR-003**: Todos os 32 security hotspots pendentes DEVEM ser revisados e marcados com resolução apropriada (SAFE, FIXED ou ACKNOWLEDGED)
- **FR-004**: As dependências de GitHub Actions que usam tags de versão DEVEM ser substituídas por SHA completo do commit correspondente, para prevenir ataques de supply chain
- **FR-005**: O bloco de código comentado em `test_schema.py` DEVE ser removido
- **FR-006**: O bloco `except` vazio em `main_window.py` DEVE receber tratamento adequado (logging ou re-raise)
- **FR-007**: A keyword `async` desnecessária em `test_scheduling_use_cases.py` DEVE ser removida ou o `await` faltante adicionado
- **FR-008**: Os métodos camelCase em `headless_mocks.py` que mimetizam a API Qt NÃO DEVEM ser renomeados — DEVEM ser suprimidos via exclusão do arquivo `tests/headless_mocks.py` das regras S100 e S116 no `sonar-project.properties`
- **FR-009**: A permissão de workflow em `publish.yml` DEVE ser revisada, especificando apenas os secrets necessários ou documentando a justificativa
- **FR-010**: Nenhuma refatoração ou correção DEVE introduzir regressão nos testes existentes

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O Quality Gate do projeto muda de ERROR para OK após todas as correções
- **SC-002**: 100% dos security hotspots estão revisados (saindo de 0% para 100%)
- **SC-003**: Zero issues CRITICAL (S3776) abertas — todas as 6 funções com complexidade ≤15
- **SC-004**: Zero issues MAJOR abertas — código comentado removido
- **SC-005**: Zero issues MINOR abertas ou todas adequadamente suprimidas
- **SC-006**: Total de issues OPEN no projeto reduzido de 20 para 0
- **SC-007**: Todas as suítes de testes continuam passando sem regressão após as mudanças
- **SC-008**: Total de security hotspots TO_REVIEW reduzido de 32 para 0

## Assumptions

- A suíte de testes existente é suficientemente abrangente para detectar regressões nas refatorações de complexidade cognitiva
- Os SHA de commit das GitHub Actions podem ser obtidos das releases oficiais de cada action
- A supressão de naming conventions nos mocks Qt é a abordagem correta, pois os nomes camelCase são necessários para compatibilidade com a API PySide6/Qt
- Os hotspots de pseudo-random em `seed_test_backlog.py` são seguros pois o script gera dados de teste, não dados sensíveis
- Os hotspots de diretórios públicos em testes usando `tmp_path` do pytest são seguros pois os diretórios são temporários e controlados pelo framework de testes
