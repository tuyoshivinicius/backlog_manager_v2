# Feature Specification: Resolucao de Issues SonarQube para Quality Gate

**Feature Branch**: `035-sonarqube-issues-resolution`
**Created**: 2026-04-01
**Status**: Draft
**Input**: User description: "Resolver todas as issues abertas e security hotspots no SonarQube para passar o quality gate do projeto"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Resolver Issue Critica de Complexidade Cognitiva (Priority: P1)

Como desenvolvedor responsavel pela qualidade do codigo, quero reduzir a complexidade cognitiva da funcao `_generate_inter_wave_deps()` no script de seed para que o SonarQube nao reporte mais violacao da regra S3776 (complexidade cognitiva maxima de 15).

**Why this priority**: E a unica issue de severidade CRITICAL no projeto. Issues criticas bloqueiam diretamente a aprovacao do quality gate e indicam codigo dificil de manter. A funcao atual tem complexidade 16 (limite e 15).

**Independent Test**: Pode ser testado executando o script de seed e verificando que o comportamento de geracao de dependencias inter-wave permanece identico. Apos re-analise no SonarQube, a issue S3776 nao deve mais aparecer.

**Acceptance Scenarios**:

1. **Given** a funcao `_generate_inter_wave_deps()` com complexidade cognitiva 16, **When** a funcao e refatorada extraindo logica para funcao auxiliar, **Then** a complexidade cognitiva cai para 15 ou menos
2. **Given** o script de seed refatorado, **When** executado com o mesmo seed fixo, **Then** os dados gerados sao identicos ao comportamento anterior (mesmas dependencias criadas)
3. **Given** a suite de testes existente, **When** executada apos a refatoracao, **Then** todos os testes passam sem falhas

---

### User Story 2 - Revisar Security Hotspot de Gerador Pseudoaleatorio (Priority: P1)

Como responsavel pela seguranca do projeto, quero revisar o security hotspot da regra S2245 (uso de gerador pseudoaleatorio) no arquivo `seed_test_backlog.py` e marca-lo como SAFE no SonarQube, pois o uso de `random` neste contexto e intencional e seguro.

**Why this priority**: O security hotspot pendente de review e a causa direta da falha do quality gate. A condicao `new_security_hotspots_reviewed` esta em 94.4% (threshold: 100%). Resolver este item e obrigatorio para passar o gate.

**Independent Test**: Pode ser testado verificando no SonarQube que o hotspot foi revisado e marcado como SAFE, e que a metrica `new_security_hotspots_reviewed` subiu para 100%.

**Acceptance Scenarios**:

1. **Given** um security hotspot TO_REVIEW na linha 572 de `seed_test_backlog.py`, **When** revisado e marcado como SAFE com justificativa, **Then** o hotspot muda para status REVIEWED com resolucao SAFE
2. **Given** o hotspot marcado como SAFE, **When** o quality gate e re-avaliado, **Then** a condicao `new_security_hotspots_reviewed` atinge 100%

---

### User Story 3 - Tratar Issues de Convencao de Nomes em Mocks Qt (Priority: P2)

Como mantenedor do projeto, quero marcar as 11 issues MINOR de convencao de nomes (regras S100 e S116) no arquivo `tests/headless_mocks.py` como ACCEPTED (Won't Fix) no SonarQube, pois os nomes em camelCase/PascalCase sao obrigatorios para compatibilidade com a API Qt/PySide6.

**Why this priority**: Embora nao bloqueiem o quality gate diretamente, estas 11 issues poluem o painel de issues abertas e podem mascarar problemas reais futuros. Sao falso-positivos no contexto de mocks Qt.

**Independent Test**: Pode ser testado verificando no SonarQube que as 11 issues mudaram de status OPEN para ACCEPTED, e que o total de issues abertas caiu de 12 para 1 (antes da correcao da P1) ou 0 (apos).

**Acceptance Scenarios**:

1. **Given** 9 issues OPEN da regra S100 (metodos camelCase) em `headless_mocks.py`, **When** marcadas como ACCEPTED com justificativa de compatibilidade Qt, **Then** as issues nao aparecem mais como OPEN
2. **Given** 2 issues OPEN da regra S116 (fields PascalCase) em `headless_mocks.py`, **When** marcadas como ACCEPTED com justificativa de compatibilidade Qt, **Then** as issues nao aparecem mais como OPEN
3. **Given** todas as 11 issues tratadas, **When** o painel de issues e consultado, **Then** apenas issues genuinas (se houver) aparecem como abertas

---

### Edge Cases

- O que acontece se a refatoracao da funcao alterar o comportamento de geracao de dados? Deve-se garantir determinismo com seed fixo.
- O que acontece se o SonarQube rejeitar a marcacao de hotspot como SAFE? Deve-se fornecer justificativa tecnica adequada.
- O que acontece se novas issues surgirem apos a re-analise? Devem ser tratadas no mesmo escopo se forem relacionadas aos arquivos modificados.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE refatorar a funcao `_generate_inter_wave_deps()` em `scripts/seed_test_backlog.py` para reduzir sua complexidade cognitiva de 16 para 15 ou menos, extraindo logica para funcao(oes) auxiliar(es)
- **FR-002**: A refatoracao DEVE preservar o comportamento exato da funcao original — dado o mesmo seed aleatorio, os mesmos dados de dependencia devem ser gerados
- **FR-003**: O security hotspot S2245 (pseudorandom number generator) na linha 572 de `seed_test_backlog.py` DEVE ser revisado e marcado como SAFE no SonarQube, com justificativa documentando que o uso de `random` com seed fixo e intencional para geracao de dados de teste
- **FR-004**: As 9 issues da regra S100 (naming convention para metodos) em `tests/headless_mocks.py` DEVEM ser marcadas como ACCEPTED no SonarQube, com justificativa de compatibilidade com a API Qt
- **FR-005**: As 2 issues da regra S116 (naming convention para fields) em `tests/headless_mocks.py` DEVEM ser marcadas como ACCEPTED no SonarQube, com justificativa de compatibilidade com a API Qt
- **FR-006**: Todos os testes existentes DEVEM continuar passando apos as modificacoes
- **FR-007**: O quality gate do projeto DEVE passar (status OK) apos todas as acoes serem concluidas e a re-analise executada

### Key Entities

- **Issue SonarQube**: Problema de qualidade de codigo identificado pelo SonarQube, com severidade (CRITICAL, MINOR), regra associada (S3776, S100, S116), status (OPEN, ACCEPTED) e localizacao no codigo
- **Security Hotspot**: Ponto de codigo que requer revisao de seguranca, com status (TO_REVIEW, REVIEWED), resolucao (SAFE, FIXED, ACKNOWLEDGED) e categoria de seguranca (weak-cryptography)
- **Quality Gate**: Conjunto de condicoes que o projeto deve atender para ser considerado com qualidade aceitavel, incluindo metricas como security hotspots reviewed (threshold: 100%)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O quality gate do projeto muda de status ERROR para OK
- **SC-002**: A metrica `new_security_hotspots_reviewed` atinge 100% (atualmente em 94.4%)
- **SC-003**: O numero total de issues abertas no projeto cai de 12 para 0
- **SC-004**: Todos os testes existentes passam sem falhas apos as modificacoes (taxa de sucesso de 100%)
- **SC-005**: O script de seed gera dados identicos antes e apos a refatoracao quando executado com o mesmo seed fixo

## Assumptions

- O SonarQube permite marcar hotspots como SAFE e issues como ACCEPTED via API/MCP tools sem necessidade de aprovacao adicional
- A refatoracao da funcao de complexidade cognitiva pode ser feita extraindo o loop interno para uma funcao auxiliar sem efeitos colaterais
- O seed fixo (`random.seed(RANDOM_SEED)`) garante que a refatoracao nao altera o comportamento observavel da geracao de dados
- Nenhuma alteracao de schema de banco de dados e necessaria — o escopo e puramente de qualidade de codigo e configuracao SonarQube

## Scope Boundaries

### Included

- Refatoracao de `_generate_inter_wave_deps()` para reduzir complexidade cognitiva
- Review e marcacao do security hotspot S2245 como SAFE
- Marcacao das 11 issues MINOR de naming convention como ACCEPTED
- Verificacao de que todos os testes passam apos as modificacoes

### Excluded

- Correcao de issues em outros arquivos nao listados
- Alteracoes no schema do banco de dados
- Adicao de novos testes (apenas garantir que os existentes passam)
- Configuracao ou alteracao de regras do quality gate no SonarQube
