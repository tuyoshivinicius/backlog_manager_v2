# EP-001 — Fundação e Persistência

**Camada:** Fundação

---

## Problema que Resolve

Antes de implementar qualquer lógica de negócio, o projeto necessita de uma infraestrutura técnica sólida: estrutura de diretórios seguindo Clean Architecture, banco de dados SQLite com schema das 4 tabelas (Story, Story_Dependency, Developer, Feature conforme §6.4), hierarquia de exceções customizadas (§7.3), sistema de logging (RNF-CONF-005), e configuração de ferramentas de qualidade de código (RNF-MANT-001 a 004). Sem essa fundação, os épicos subsequentes não teriam onde se apoiar.

## Objetivo (Valor Mensurável)

Estabelecer a infraestrutura técnica que permite o desenvolvimento de todas as 7 capacidades do produto (SRS §2.2). Ao final deste épico:
- Projeto Python configurado com estrutura de 4 camadas (UI → Services → Domain → Repository)
- Banco SQLite operacional com schema completo
- Sistema de exceções pronto para uso pelos serviços
- Logging configurado em AppData com rotação
- Pipeline de qualidade (pytest, black, isort, pydocstyle) configurado

## Alinhamento Estratégico

Este épico habilita **todas as 7 capacidades** do produto (§2.2) ao fornecer:
- Persistência para Gestão de Backlog, Features e Desenvolvedores (capacidades 1, 2, 3)
- Infraestrutura de exceções para Gestão de Dependências (capacidade 4)
- Base de dados para Cálculo de Cronograma e Alocação Automática (capacidades 5, 6)
- Estrutura de repositórios para Integração Excel (capacidade 7)

## Personas Impactadas

| Persona (SRS §2.3) | Impacto |
|--------------------|---------|
| Scrum Master / Tech Lead | Indiretamente — fundação técnica que suporta todas as funcionalidades futuras |
| Gerente de Projeto | Indiretamente — garantia de confiabilidade e integridade de dados |
| Product Owner | Indiretamente — base para persistência do backlog priorizado |

## Jornadas / Casos de Uso Afetados

- UC-001: Criar e Priorizar Backlog — Contribui para (completo em EP-003/EP-008)
- UC-002: Alocação Automática — Contribui para (completo em EP-007/EP-008)
- UC-003: Detectar e Resolver Deadlock — Contribui para (completo em EP-005)
- UC-004: Importar Backlog do Excel — Contribui para (completo em EP-009)
- UC-005: Gerenciar Ondas de Entrega — Contribui para (completo em EP-004/EP-008)
- CT-001 a CT-005: Parcial — infraestrutura de testes configurada

---

## Escopo

### Dentro do Escopo

**Requisitos Funcionais:**
- Nenhum RF é escopo principal deste épico (épico de infraestrutura)

**Requisitos Não-Funcionais:**
- RNF-MANT-001: Cobertura de testes ≥ 80% (configuração pytest-cov)
- RNF-MANT-002: Docstrings Google Style (configuração pydocstyle)
- RNF-MANT-003: Complexidade ciclomática ≤ 10 (configuração radon/flake8)
- RNF-MANT-004: PEP 8, Black, isort, type hints (configuração pre-commit)
- RNF-CONF-003: Integridade de dados — transações ACID SQLite, foreign keys enforced
- RNF-CONF-004: Persistência imediata — auto-save após operações
- RNF-CONF-005: Sistema de logs em AppData, rotação 10MB, retenção 3 arquivos
- RNF-SEG-001: Validação de entrada — prepared statements SQLite
- RNF-SEG-003: Arquivos locais — banco em AppData com permissões do usuário

**Artefatos Estruturais do SRS:**
- Schema ER (§6.4): Implementação das 4 tabelas (Story, Story_Dependency, Developer, Feature) com relacionamentos e constraints
- Hierarquia de Exceções (§7.3): BacklogManagerException, DependencyException, FeatureException, AllocationException, e warnings (DeadlockWarning, IdlenessWarning, etc.)

### Fora do Escopo

- RF-STORY-* → será tratado em EP-002 e EP-003
- RF-DEV-* → será tratado em EP-004
- RF-FEAT-* → será tratado em EP-004
- RF-DEP-* → será tratado em EP-005
- RF-SCHED-* → será tratado em EP-006
- RF-ALOC-* → será tratado em EP-007
- Interface gráfica PySide6 → será tratada em EP-008

---

## Requisitos Funcionais Principais

| ID | Nome | Prioridade |
|----|------|------------|
| — | Este épico não possui RFs como escopo principal | — |

## Requisitos Não-Funcionais Críticos

| ID | Nome | Métrica-alvo |
|----|------|-------------|
| RNF-MANT-001 | Cobertura de Testes | ≥ 80% linhas, 100% em core |
| RNF-MANT-002 | Docstrings | Google Style em classes/métodos públicos |
| RNF-MANT-003 | Complexidade Ciclomática | ≤ 10 por função (≤ 15 para alocação) |
| RNF-MANT-004 | Padronização de Código | PEP 8, Black (88 cols), isort, type hints |
| RNF-CONF-003 | Integridade de Dados | Transações ACID, FKs enforced |
| RNF-CONF-004 | Persistência Automática | Commit imediato após operações |
| RNF-CONF-005 | Sistema de Logs | Rotação 10MB, retenção 3 arquivos |
| RNF-SEG-001 | Validação de Entrada | Prepared statements em 100% das queries |
| RNF-SEG-003 | Proteção de Arquivos | Banco em AppData, permissões de usuário |

---

## Critérios de Aceite (Alto Nível)

- [ ] **Dado** um novo ambiente de desenvolvimento, **Quando** executo `pip install -e .`, **Então** todas as dependências são instaladas e o projeto é importável
- [ ] **Dado** o schema ER definido em §6.4, **Quando** inicializo o banco, **Então** as 4 tabelas são criadas com todas as constraints (PKs, FKs, CHECKs, UNIQUEs)
- [ ] **Dado** a hierarquia de exceções de §7.3, **Quando** importo o módulo de exceções, **Então** todas as exceções customizadas estão disponíveis com herança correta
- [ ] **Dado** o sistema de logging configurado, **Quando** uma operação crítica é executada, **Então** o log é gravado em AppData com formato e rotação corretos
- [ ] **Dado** pre-commit hooks configurados, **Quando** faço commit, **Então** black, isort, e linters são executados automaticamente

## KPIs / Métricas de Sucesso

| KPI | Métrica | Meta | Fonte SRS |
|-----|---------|------|-----------|
| Cobertura de código | % linhas cobertas por testes | ≥ 80% | RNF-MANT-001 |
| Docstring coverage | % classes/métodos documentados | 100% públicos | RNF-MANT-002 |
| Complexidade máxima | CC por função | ≤ 10 | RNF-MANT-003 |
| Conformidade PEP 8 | Warnings do flake8 | 0 | RNF-MANT-004 |
| Integridade referencial | FK violations | 0 | RNF-CONF-003 |

## Plano de Validação

| Tipo | Descrição | Referência SRS |
|------|-----------|----------------|
| Testes Unitários | Testar criação de banco e schema | RNF-CONF-003 |
| Testes Unitários | Testar hierarquia de exceções e mensagens | §7.3 |
| Testes Integração | Testar operações CRUD básicas em cada tabela | RNF-CONF-003/004 |
| Testes Integração | Verificar foreign keys e constraints | §6.4 |
| Teste Manual | Verificar criação de logs em AppData | RNF-CONF-005 |
| Revisão de Código | Validar estrutura de camadas (Clean Architecture) | §6.1 |
| Revisão de Código | Verificar pre-commit hooks funcionando | RNF-MANT-004 |

---

## Dependências

*Sem dependências* — este é o primeiro épico e estabelece a fundação para todos os demais.

## Riscos e Premissas

| Tipo | Descrição | Mitigação |
|------|-----------|-----------|
| Premissa | Python 3.11+ disponível no ambiente de desenvolvimento | Documentar requisitos em README |
| Premissa | PySide6 6.6.1+ compatível com Windows 10/11 | Testar em ambas as versões durante setup |
| Risco | Schema do banco pode precisar de ajustes durante implementação dos épicos seguintes | Criar migrations simples ou script de recriação para fase de desenvolvimento |
| Risco | Conflito entre dependências Python (PySide6 vs outras libs) | Usar ambiente virtual isolado (venv) |
| Premissa | Diretório AppData acessível para logs e banco (§2.5) | Verificar permissões na inicialização |
