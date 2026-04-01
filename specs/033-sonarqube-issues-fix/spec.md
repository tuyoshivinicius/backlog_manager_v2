# Feature Specification: Resolução de Issues SonarQube

**Feature Branch**: `033-sonarqube-issues-fix`
**Created**: 2026-04-01
**Status**: Draft
**Input**: User description: "Resolução de 117 issues SonarQube organizadas por severidade (BLOCKER, CRITICAL, MAJOR, MINOR) incluindo refatoração de complexidade cognitiva, correção de bugs potenciais, limpeza de código e adequação a convenções"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Correção de Bug Potencial por Retorno Constante (Priority: P1)

Como desenvolvedor, preciso que métodos que sempre retornam o mesmo valor sejam refatorados para eliminar lógica desnecessária e prevenir bugs em runtime.

**Why this priority**: A issue BLOCKER indica um potencial bug em runtime onde um método sempre retorna o mesmo valor, podendo causar comportamento inesperado em produção.

**Independent Test**: Pode ser testado verificando que o método refatorado mantém o comportamento esperado em todos os cenários de uso existentes, e que testes unitários cobrem os caminhos de execução.

**Acceptance Scenarios**:

1. **Given** o método em `story_table_model.py` linha 178 sempre retorna o mesmo valor, **When** o método é refatorado, **Then** o comportamento do sistema permanece idêntico e a issue S3516 é resolvida no SonarQube
2. **Given** o método refatorado, **When** todos os testes existentes são executados, **Then** nenhum teste falha

---

### User Story 2 - Correção de Tasks Async sem Referência (Priority: P2)

Como desenvolvedor, preciso que tasks assíncronas criadas em ViewModels e Views mantenham referências para evitar garbage collection prematura, prevenindo bugs intermitentes em produção.

**Why this priority**: 12 issues MAJOR (S7502) indicam que tasks asyncio podem ser coletadas pelo garbage collector antes de completarem, causando falhas silenciosas e comportamento inconsistente na UI.

**Independent Test**: Pode ser testado verificando que todas as tasks assíncronas mantêm referências válidas durante todo seu ciclo de vida e que operações async completam sem serem interrompidas.

**Acceptance Scenarios**:

1. **Given** tasks asyncio criadas sem referência em ViewModels/Views, **When** as tasks são refatoradas para manter referências, **Then** nenhuma task é coletada prematuramente pelo garbage collector
2. **Given** o padrão corrigido, **When** operações assíncronas são disparadas na UI, **Then** todas completam com sucesso sem falhas silenciosas

---

### User Story 3 - Correção de CancelledError Silenciado (Priority: P3)

Como desenvolvedor, preciso que exceções CancelledError sejam propagadas corretamente para garantir o cancelamento adequado de operações assíncronas.

**Why this priority**: 4 issues MAJOR (S7497) indicam que o cancelamento de tasks asyncio está sendo silenciado, podendo causar estados inconsistentes quando o usuário cancela operações.

**Independent Test**: Pode ser testado verificando que CancelledError é re-raised nos handlers de exceção afetados e que o cancelamento de operações funciona corretamente.

**Acceptance Scenarios**:

1. **Given** handlers que capturam CancelledError sem re-raise, **When** os handlers são corrigidos, **Then** CancelledError é propagado corretamente após limpeza de recursos
2. **Given** uma operação assíncrona em execução, **When** o usuário cancela a operação, **Then** o cancelamento é processado sem deixar estados inconsistentes

---

### User Story 4 - Redução de Complexidade Cognitiva em Código de Produção (Priority: P4)

Como desenvolvedor, preciso que métodos com complexidade cognitiva excessiva (acima do limite de 15) sejam refatorados em código de produção para facilitar manutenção e reduzir risco de bugs.

**Why this priority**: 12 issues CRITICAL (S3776) em código de produção indicam métodos excessivamente complexos que dificultam revisão de código, testes e manutenção. Complexidades chegam a 79 pontos (limite: 15).

**Independent Test**: Pode ser testado verificando que cada método refatorado mantém comportamento idêntico ao original (testes existentes passam) e que a complexidade cognitiva medida pelo SonarQube fica dentro do limite.

**Acceptance Scenarios**:

1. **Given** métodos com complexidade cognitiva > 15 em código de produção, **When** os métodos são refatorados em submétodos menores, **Then** a complexidade de cada método fica ≤ 15 e o comportamento é preservado
2. **Given** métodos refatorados, **When** testes de regressão são executados, **Then** todos os testes passam sem alterações

---

### User Story 5 - Redução de Complexidade Cognitiva em Scripts (Priority: P5)

Como desenvolvedor, preciso que scripts utilitários com complexidade cognitiva excessiva sejam refatorados para facilitar manutenção.

**Why this priority**: 5 issues CRITICAL (S3776) em scripts (`extract_metrics.py`, `seed_test_backlog.py`) com complexidades de até 96 pontos precisam ser decompostas, mas têm menor impacto que código de produção.

**Independent Test**: Pode ser testado verificando que os scripts refatorados produzem os mesmos resultados e que a complexidade fica dentro do limite.

**Acceptance Scenarios**:

1. **Given** scripts com complexidade cognitiva > 15, **When** as funções são decompostas, **Then** a complexidade de cada função fica ≤ 15
2. **Given** scripts refatorados, **When** executados com os mesmos inputs, **Then** produzem outputs idênticos aos originais

---

### User Story 6 - Correção de Literal Duplicado e Type Hint (Priority: P6)

Como desenvolvedor, preciso que literais duplicados sejam extraídos para constantes e type hints incorretos sejam corrigidos para melhorar a manutenção do código.

**Why this priority**: 1 issue CRITICAL (S1192) de literal duplicado 4x e 1 issue MAJOR (S5890) de type hint incorreto são correções rápidas que melhoram a qualidade do código.

**Independent Test**: Pode ser testado verificando que a constante extraída é usada em todos os locais anteriormente duplicados e que o type hint correto é aceito pelo verificador de tipos.

**Acceptance Scenarios**:

1. **Given** a string "UnitOfWork must be used as context manager" duplicada 4x, **When** extraída para constante, **Then** todos os 4 usos referenciam a constante
2. **Given** type hint incorreto em `theme.py`, **When** corrigido para `Optional[IconManager]`, **Then** o verificador de tipos não reporta erros

---

### User Story 7 - Adição de Comentários em Métodos Vazios de Testes (Priority: P7)

Como desenvolvedor, preciso que métodos vazios em mocks e fixtures de teste tenham comentários explicativos ou markers de intenção para indicar que a ausência de implementação é deliberada.

**Why this priority**: 19 issues CRITICAL (S1186) em código de teste. Embora não afetem produção, são necessários para conformidade com as regras de qualidade.

**Independent Test**: Pode ser testado verificando que cada método anteriormente vazio agora tem um comentário docstring ou `pass` com comentário explicativo, e que as issues são resolvidas no SonarQube.

**Acceptance Scenarios**:

1. **Given** métodos vazios em mocks de teste sem comentário, **When** comentários explicativos são adicionados, **Then** a intenção de cada método vazio está documentada
2. **Given** métodos corrigidos, **When** SonarQube re-analisa, **Then** issues S1186 são resolvidas

---

### User Story 8 - Correção de Comparações Float em Testes (Priority: P8)

Como desenvolvedor, preciso que comparações de ponto flutuante em testes usem tolerância adequada para evitar falhas intermitentes por imprecisão numérica.

**Why this priority**: 15 issues MAJOR (S1244) indicam comparações diretas de float que podem causar falhas flaky em testes.

**Independent Test**: Pode ser testado verificando que todas as comparações de float usam tolerância adequada e que os testes passam de forma consistente.

**Acceptance Scenarios**:

1. **Given** comparações diretas de float em testes (`==`), **When** substituídas por comparações com tolerância, **Then** testes são resilientes a imprecisão de ponto flutuante
2. **Given** testes corrigidos, **When** executados múltiplas vezes, **Then** resultados são consistentes

---

### User Story 9 - Limpeza de Código: Blocos Vazios, Parâmetros e Variáveis Não Usados (Priority: P9)

Como desenvolvedor, preciso que blocos vazios, parâmetros não utilizados e variáveis não usadas sejam limpos para reduzir ruído no código e melhorar a legibilidade.

**Why this priority**: 12 issues MAJOR (S108/S1172/S1854) e 9 issues MINOR (S1481) representam limpeza de código que melhora a qualidade geral mas tem baixo risco.

**Independent Test**: Pode ser testado verificando que o código removido/alterado não era utilizado e que todos os testes continuam passando.

**Acceptance Scenarios**:

1. **Given** blocos de código vazios sem comentário, **When** são removidos ou documentados, **Then** issues S108 são resolvidas
2. **Given** parâmetros e variáveis não usados, **When** são removidos ou prefixados com `_`, **Then** issues S1172/S1854/S1481 são resolvidas
3. **Given** código comentado, **When** removido, **Then** issue S125 é resolvida

---

### User Story 10 - Adequação a Convenções e Otimizações Menores (Priority: P10)

Como desenvolvedor, preciso que convenções de naming sejam respeitadas (com exceções documentadas para overrides de Qt), funções async desnecessárias sejam simplificadas e padrões idiomáticos sejam aplicados.

**Why this priority**: 31 issues MINOR representam polimento de código. Naming conventions em mocks Qt são falsos positivos que precisam ser documentados ou suprimidos. Funções async desnecessárias e uso de `dict.fromkeys()` são otimizações simples.

**Independent Test**: Pode ser testado verificando que convenções são aplicadas onde possível, falsos positivos são suprimidos com comentário, e otimizações são aplicadas sem alterar comportamento.

**Acceptance Scenarios**:

1. **Given** métodos camelCase que são overrides de Qt, **When** documentados com comentário explicativo ou supressão, **Then** issues de naming são resolvidas ou justificadamente suprimidas
2. **Given** funções async sem uso de await, **When** convertidas para funções síncronas, **Then** issues S7503 são resolvidas
3. **Given** construções que podem usar `dict.fromkeys()`, **When** refatoradas, **Then** issues S7519 são resolvidas

---

### Edge Cases

- O que acontece se a refatoração de complexidade cognitiva alterar a assinatura pública de um método? A interface pública deve ser preservada.
- Como lidar com métodos vazios em mocks que são overrides obrigatórios de classes base Qt? Devem receber docstring explicando que são stubs intencionais.
- O que fazer com parâmetros não usados que fazem parte de uma interface/contrato? Devem ser prefixados com `_` para indicar uso intencional.
- Como garantir que a remoção de `async` de funções não quebra chamadores que usam `await`? Verificar todos os call sites antes da remoção.
- O que acontece se um método de alta complexidade não puder ser decomposto sem alterar o comportamento? Documentar a justificativa e usar supressão com comentário.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE refatorar o método em `story_table_model.py:178` (S3516 BLOCKER) para eliminar retorno constante sem alterar comportamento externo
- **FR-002**: O sistema DEVE manter referências para todas as tasks asyncio criadas em ViewModels e Views (12 issues S7502) para prevenir garbage collection prematura
- **FR-003**: O sistema DEVE re-raise CancelledError em todos os handlers de exceção que o capturam (4 issues S7497) após executar limpeza de recursos
- **FR-004**: O sistema DEVE reduzir a complexidade cognitiva de 17 métodos/funções (S3776) para ≤ 15, preservando comportamento idêntico
- **FR-005**: O sistema DEVE extrair a string "UnitOfWork must be used as context manager" (S1192) para uma constante reutilizável
- **FR-006**: O sistema DEVE corrigir o type hint em `theme.py:385` (S5890) para usar a forma correta de tipo opcional
- **FR-007**: O sistema DEVE adicionar comentários explicativos ou docstrings em 19 métodos vazios de teste (S1186) indicando que a ausência de implementação é intencional
- **FR-008**: O sistema DEVE substituir 15 comparações diretas de float em testes (S1244) por comparações com tolerância adequada
- **FR-009**: O sistema DEVE resolver 7 blocos de código vazios (S108) com remoção ou documentação
- **FR-010**: O sistema DEVE resolver 5 parâmetros/variáveis não utilizados (S1172/S1854) por remoção ou prefixo `_`
- **FR-011**: O sistema DEVE remover código comentado identificado (S125)
- **FR-012**: O sistema DEVE documentar ou suprimir 13 issues de naming convention (S100/S116) que são falsos positivos por overrides Qt
- **FR-013**: O sistema DEVE converter 7 funções async desnecessárias (S7503) para funções síncronas, verificando todos os call sites
- **FR-014**: O sistema DEVE aplicar padrão `dict.fromkeys()` onde recomendado (S7519)
- **FR-015**: O sistema DEVE remover 9 variáveis locais não usadas em testes (S1481) e 1 uso desnecessário de `list()` (S7504)
- **FR-016**: Todas as alterações DEVEM preservar o comportamento existente — nenhum teste existente deve falhar
- **FR-017**: Todas as alterações DEVEM passar nas verificações de linting (`ruff check .`)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% das 117 issues identificadas no SonarQube são resolvidas ou justificadamente suprimidas com documentação
- **SC-002**: 0 issues BLOCKER permanecem no projeto após a conclusão
- **SC-003**: 0 issues CRITICAL permanecem no projeto após a conclusão (exceto falsos positivos documentados)
- **SC-004**: Todos os testes existentes continuam passando sem modificação de lógica de teste (apenas ajustes de precisão float são permitidos)
- **SC-005**: Nenhum novo issue é introduzido pelo SonarQube como resultado das correções
- **SC-006**: Complexidade cognitiva de todos os métodos refatorados fica ≤ 15 conforme medido pelo SonarQube
- **SC-007**: Verificações de linting (`/ruff check .`) passam sem erros após todas as alterações

## Assumptions

- Issues de naming convention (S100/S116) em métodos que são overrides de classes Qt são falsos positivos e serão tratados com supressão documentada, não com renomeação
- A refatoração de complexidade cognitiva pode ser feita por decomposição em submétodos privados sem alterar interfaces públicas
- O padrão para manter referências de tasks asyncio será armazenar em um conjunto (`set`) no nível da instância, usando callbacks `add_done_callback` para limpeza automática
- Comparações de float em testes serão corrigidas usando `pytest.approx()` como mecanismo de tolerância
- Scripts utilitários (`extract_metrics.py`, `seed_test_backlog.py`, `validate_allocation_data.py`) podem ser refatorados livremente pois não fazem parte da API pública do sistema
