# EP-009 — Integração Excel

**Camada:** Integração & Otimização

---

## Problema que Resolve

Muitas equipes já possuem backlogs em planilhas Excel ou precisam exportar dados para relatórios e apresentações. Este épico implementa a funcionalidade de importação e exportação de dados via arquivos Excel (.xlsx), permitindo interoperabilidade com outras ferramentas e servindo como mecanismo de backup manual.

## Objetivo (Valor Mensurável)

Implementar a capacidade de **Integração Excel** (§2.2 item 7):
- Importar backlog completo de arquivo Excel com formato definido
- Gerar IDs automáticos para histórias sem ID
- Validar ciclos de dependência no conjunto importado
- Exportar backlog completo para Excel
- Servir como mecanismo de backup manual (RNF-SEG-002)

## Alinhamento Estratégico

Este épico implementa diretamente a **capacidade 7**: "Integração Excel: Import/export para interoperabilidade".

Também atende ao requisito de segurança:
- **RNF-SEG-002**: Backup de dados via exportação completa

## Personas Impactadas

| Persona (SRS §2.3) | Impacto |
|--------------------|---------|
| Scrum Master / Tech Lead | Importa backlogs existentes; exporta para compartilhar |
| Product Owner | Importa priorização de outras ferramentas |
| Gerente de Projeto | Exporta dados para relatórios executivos |

## Jornadas / Casos de Uso Afetados

- UC-004: Importar Backlog do Excel — **Habilita** (fluxo principal completo)
- RNF-SEG-002: Backup Manual — **Habilita** (export completo)

---

## Escopo

### Dentro do Escopo

**Requisitos Funcionais (derivados de UC-004 e §2.2 item 7):**
- RF-EXCEL-001 (derivado): Importar arquivo Excel com formato definido
- RF-EXCEL-002 (derivado): Validar headers obrigatórios (ID, Componente, Nome, SP, Feature, Dependencias)
- RF-EXCEL-003 (derivado): Gerar ID automático (US-NNN) para linhas sem ID
- RF-EXCEL-004 (derivado): Criar/associar Features durante import
- RF-EXCEL-005 (derivado): Validar ciclos de dependência no conjunto importado
- RF-EXCEL-006 (derivado): Exportar backlog completo para Excel
- RF-EXCEL-007 (derivado): Exportar desenvolvedores e features

**Requisitos Não-Funcionais:**
- RNF-SEG-002: Backup manual via exportação completa
- RNF-SEG-004: LGPD — N/A (dados não são pessoais sensíveis)
- RNF-MANT-001 a 004: Conforme estabelecido em EP-001

**Artefatos Estruturais do SRS:**
- UC-004: Fluxo completo de importação
- Formato de arquivo: Headers na primeira linha, case-sensitive

### Fora do Escopo

- Importação de outros formatos (CSV, JSON) → fora do escopo do produto
- Integração com ferramentas externas (Jira, Azure DevOps) → fora do escopo (§1.2)
- Sincronização automática com arquivos externos → fora do escopo

---

## Requisitos Funcionais Principais

| ID | Nome | Prioridade |
|----|------|------------|
| RF-EXCEL-001 | Importar Arquivo Excel | Must Have |
| RF-EXCEL-002 | Validar Headers Obrigatórios | Must Have |
| RF-EXCEL-003 | Gerar ID Automático no Import | Must Have |
| RF-EXCEL-004 | Criar/Associar Features no Import | Must Have |
| RF-EXCEL-005 | Validar Ciclos no Import | Must Have |
| RF-EXCEL-006 | Exportar Backlog para Excel | Must Have |
| RF-EXCEL-007 | Exportar Desenvolvedores e Features | Should Have |

## Requisitos Não-Funcionais Críticos

| ID | Nome | Métrica-alvo |
|----|------|-------------|
| RNF-SEG-002 | Backup Manual | Export inclui todas as entidades |
| RNF-MANT-001 | Cobertura de Testes | Conforme EP-001 |
| RNF-MANT-002 | Docstrings | Conforme EP-001 |
| RNF-MANT-003 | Complexidade Ciclomática | Conforme EP-001 |
| RNF-MANT-004 | Padronização de Código | Conforme EP-001 |

---

## Critérios de Aceite (Alto Nível)

### Importação
- [ ] **Dado** arquivo Excel com 10 histórias válidas, **Quando** importo o arquivo, **Então** 10 histórias são criadas no sistema
- [ ] **Dado** arquivo Excel com coluna obrigatória ausente, **Quando** tento importar, **Então** sistema exibe erro e aborta
- [ ] **Dado** linha com ID vazio e Componente="AUTH", **Quando** importo, **Então** história recebe ID "US-001" (ou próximo disponível)
- [ ] **Dado** arquivo onde A depende de B e B depende de A, **Quando** tento importar, **Então** sistema exibe erro "Ciclo detectado" e nenhuma história é importada
- [ ] **Dado** Feature "Login" referenciada no Excel mas não existente, **Quando** importo, **Então** Feature "Login" é criada automaticamente

### Exportação
- [ ] **Dado** backlog com 20 histórias, 5 desenvolvedores e 3 features, **Quando** exporto para Excel, **Então** arquivo .xlsx é criado com todos os dados
- [ ] **Dado** arquivo exportado, **Quando** reimporto em instalação limpa, **Então** todos os dados são restaurados

### Backup
- [ ] **Dado** exportação completa, **Quando** abro arquivo no Excel, **Então** vejo todas as histórias, desenvolvedores e features
- [ ] **Dado** arquivo de backup, **Quando** importo em nova instalação, **Então** sistema fica idêntico ao original

## KPIs / Métricas de Sucesso

| KPI | Métrica | Meta | Fonte SRS |
|-----|---------|------|-----------|
| Import bem-sucedido | % arquivos válidos | 100% | UC-004 |
| Validação de ciclos | Ciclos detectados | 100% | UC-004 FA-4 |
| Export completo | Entidades exportadas | 100% | RNF-SEG-002 |
| Roundtrip | Export → Import | Dados idênticos | RNF-SEG-002 |

## Plano de Validação

| Tipo | Descrição | Referência SRS |
|------|-----------|----------------|
| Testes Unitários | Importar arquivo válido com N histórias | UC-004 |
| Testes Unitários | Rejeitar arquivo com header ausente | UC-004 FA-1 |
| Testes Unitários | Gerar ID para linha sem ID | UC-004 passo 6a |
| Testes Unitários | Skip linha com SP inválido (warning) | UC-004 FA-2 |
| Testes Unitários | Detectar ciclo no import | UC-004 FA-4 |
| Testes Unitários | Criar feature inexistente | UC-004 passo 6c |
| Testes Unitários | Exportar histórias completas | RF-EXCEL-006 |
| Testes Unitários | Exportar desenvolvedores e features | RF-EXCEL-007 |
| Testes Integração | Roundtrip: export → import em DB limpo | RNF-SEG-002 |
| Cenário de Teste | UC-004 completo | UC-004 |
| Teste Manual | Importar arquivo Excel real de 50 linhas | UC-004 |
| Teste Manual | Exportar e abrir no Microsoft Excel | RNF-SEG-002 |
| Revisão de Código | Validar uso de openpyxl | §2.4 |

---

## Dependências

| Épico | Motivo |
|-------|--------|
| EP-001 | Infraestrutura de persistência e openpyxl configurado |
| EP-002 | Validações de entidades aplicadas durante import |
| EP-003 | StoryService para criar histórias importadas |
| EP-004 | DeveloperService e FeatureService para criar/associar recursos |
| EP-005 | DependencyService para validar ciclos no import |
| EP-008 | Interface gráfica com botões Import/Export e diálogos de arquivo |

## Riscos e Premissas

| Tipo | Descrição | Mitigação |
|------|-----------|-----------|
| Premissa | Formato de arquivo é fixo e documentado | Documentar formato esperado; exibir erro claro se inválido |
| Premissa | Headers são case-sensitive | Documentar; considerar normalização futura |
| Risco | Arquivo Excel corrompido pode crashar openpyxl | Usar try/except e exibir erro amigável |
| Risco | Arquivo muito grande pode ser lento para importar | Limite de 500 histórias com warning (RNF-PERF-001) |
| Premissa | Export sempre sobrescreve arquivo de destino | Confirmar antes de sobrescrever |
| Risco | Dependências para IDs ainda não importados | Processar em duas passadas: criar histórias, depois dependências |
| Premissa | openpyxl é suficiente para leitura/escrita de .xlsx | Biblioteca madura e estável |
