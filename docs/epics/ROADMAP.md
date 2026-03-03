# Roadmap de Épicos — Backlog Manager v2

## Visão Geral da Sequência

| Ordem | Código | Nome | Camada | Dependências | Marco |
|-------|--------|------|--------|--------------|-------|
| 1 | EP-001 | Fundação e Persistência | Fundação | — | |
| 2 | EP-002 | Domínio Core: Entidades e Validações | Domínio Core | EP-001 | |
| 3 | EP-003 | Gestão de Backlog | Domínio Core | EP-001, EP-002 | |
| 4 | EP-004 | Gestão de Recursos | Domínio Core | EP-001, EP-002, EP-003 | |
| 5 | EP-005 | Gestão de Dependências | Serviços de Negócio | EP-001, EP-002, EP-003, EP-004 | |
| 6 | EP-006 | Cálculo de Cronograma | Serviços de Negócio | EP-001, EP-002, EP-003, EP-005 | |
| 7 | EP-007 | Motor de Alocação | Serviços de Negócio | EP-001 a EP-006 | |
| 8 | EP-008 | Interface Gráfica | Interface & Experiência | EP-001 a EP-007 | **MVP** |
| 9 | EP-009 | Integração Excel | Integração & Otimização | EP-001 a EP-008 | |

---

## Marco MVP

O produto atinge o estado de **MVP (Minimum Viable Product)** ao final do **EP-008: Interface Gráfica**.

Neste ponto, o usuário consegue realizar todas as operações essenciais definidas no contexto do projeto:

| Capacidade MVP | Épicos que Habilitam | Status após EP-008 |
|----------------|---------------------|-------------------|
| (a) Cadastrar desenvolvedores | EP-004 + EP-008 | Completo |
| (b) Criar e priorizar histórias | EP-003 + EP-008 | Completo |
| (c) Definir dependências | EP-005 + EP-008 | Completo |
| (d) Calcular cronograma | EP-006 + EP-008 | Completo |
| (e) Executar alocação automática com resultado visível | EP-007 + EP-008 | Completo |

**Features, ondas e integração Excel** são funcionalidades pós-MVP, implementadas em EP-004 (features/ondas) e EP-009 (Excel).

---

## Mapa de Dependências

```text
EP-001 (Fundação e Persistência)
  └── EP-002 (Domínio Core: Entidades)
       └── EP-003 (Gestão de Backlog)
            └── EP-004 (Gestão de Recursos)
                 └── EP-005 (Gestão de Dependências)
                      └── EP-006 (Cálculo de Cronograma)
                           └── EP-007 (Motor de Alocação)
                                └── EP-008 (Interface Gráfica) ← MVP
                                     └── EP-009 (Integração Excel)
```

**Legenda:**
- Setas indicam dependência: épico filho depende de épico pai
- Cada épico pode iniciar somente após suas dependências estarem completas
- O fluxo é linear com algumas dependências paralelas possíveis entre EP-003 e EP-004

---

## Matriz de Rastreabilidade: RF → Épico

| Requisito | Descrição Curta | Épico |
|-----------|-----------------|-------|
| RF-STORY-001 | Criar Nova História | EP-003 |
| RF-STORY-002 | Editar História Existente | EP-003 |
| RF-STORY-003 | Deletar História | EP-003 |
| RF-STORY-004 | Duplicar História | EP-003 |
| RF-STORY-005 | Listar Histórias do Backlog | EP-003 |
| RF-STORY-006 | Mover Prioridade | EP-003 |
| RF-STORY-007 | Atribuir Desenvolvedor Manualmente | EP-003 |
| RF-STORY-008 | Validar Story Points | EP-002 |
| RF-STORY-009 | Gerenciar Status da História | EP-002 |
| RF-STORY-010 | Validar Invariantes da História | EP-002 |
| RF-DEV-001 | Cadastrar Novo Desenvolvedor | EP-004 |
| RF-DEV-002 | Editar Desenvolvedor | EP-004 |
| RF-DEV-003 | Deletar Desenvolvedor | EP-004 |
| RF-DEV-004 | Listar Desenvolvedores | EP-004 |
| RF-FEAT-001 | Criar Nova Feature | EP-004 |
| RF-FEAT-002 | Editar Feature | EP-004 |
| RF-FEAT-003 | Deletar Feature | EP-004 |
| RF-FEAT-004 | Associar Histórias a Features | EP-004 |
| RF-FEAT-005 | Validar Onda Única | EP-004 |
| RF-DEP-001 | Adicionar Dependência entre Histórias | EP-005 |
| RF-DEP-002 | Remover Dependência | EP-005 |
| RF-DEP-003 | Detectar Ciclos de Dependência | EP-005 |
| RF-DEP-004 | Validar Dependências entre Ondas | EP-005 |
| RF-SCHED-001 | Calcular Duração da História | EP-006 |
| RF-SCHED-002 | Calcular com Dias Úteis | EP-006 |
| RF-SCHED-003 | Excluir Feriados Nacionais | EP-006 |
| RF-SCHED-004 | Sequenciar por Dependências | EP-006 |
| RF-SCHED-005 | Ajustar para Dia Útil | EP-006 |
| RF-SCHED-006 | Ordenar Backlog Topologicamente | EP-006 |
| RF-ALOC-001 | Executar Alocação Automática | EP-007 |
| RF-ALOC-002 | Balanceamento de Carga | EP-007 |
| RF-ALOC-003 | Critério Proprietário de Dependência | EP-007 |
| RF-ALOC-004 | Evitar Conflitos de Período | EP-007 |
| RF-ALOC-005 | Ajustar Datas por Indisponibilidade | EP-007 |
| RF-ALOC-006 | Processar por Ondas | EP-007 |
| RF-ALOC-007 | Detectar Deadlocks | EP-007 |
| RF-ALOC-008 | Detectar Ociosidade | EP-007 |
| RF-ALOC-009 | Configurar Limite de Ociosidade | EP-007 |
| RF-ALOC-010 | Realocar para Minimizar Ociosidade | EP-007 |
| RF-ALOC-011 | Coletar Métricas de Alocação | EP-007 |
| RF-ALOC-012 | Validação e Estabilização Pós-Alocação | EP-007 |
| RF-ALOC-013 | Limites de Segurança do Algoritmo | EP-007 |

> **Total: 42 RFs cobertos** (10 RF-STORY + 4 RF-DEV + 5 RF-FEAT + 4 RF-DEP + 6 RF-SCHED + 13 RF-ALOC)

---

## Matriz de Rastreabilidade: RNF → Épico(s)

| Requisito | Descrição Curta | Épico(s) |
|-----------|-----------------|----------|
| RNF-PERF-001 | Tempo de Alocação ≤ 5s | EP-007 |
| RNF-PERF-002 | Responsividade UI ≤ 100ms | EP-008 |
| RNF-PERF-003 | Consumo de Memória ≤ 150MB | EP-007 |
| RNF-PERF-004 | Tempo de Startup ≤ 3s | EP-008 |
| RNF-USAB-001 | Plataforma Windows 10/11 | EP-008 |
| RNF-USAB-002 | Resolução Mínima 1366x768 | EP-008 |
| RNF-USAB-003 | Acessibilidade Básica | EP-008 |
| RNF-USAB-004 | Curva de Aprendizado ≤ 15min | EP-008 |
| RNF-CONF-001 | Disponibilidade 99% | EP-008 |
| RNF-CONF-002 | Recuperação de Erros | EP-008 |
| RNF-CONF-003 | Integridade de Dados (ACID) | EP-001 |
| RNF-CONF-004 | Persistência Automática | EP-001 |
| RNF-CONF-005 | Sistema de Logs | EP-001 |
| RNF-SEG-001 | Validação de Entrada | EP-001 |
| RNF-SEG-002 | Backup Manual | EP-009 |
| RNF-SEG-003 | Proteção de Arquivos | EP-001 |
| RNF-SEG-004 | LGPD (N/A) | EP-009 (documentado) |
| RNF-MANT-001 | Cobertura de Testes ≥ 80% | EP-001 (estabelecido), todos (aplicado) |
| RNF-MANT-002 | Docstrings Google Style | EP-001 (estabelecido), todos (aplicado) |
| RNF-MANT-003 | Complexidade Ciclomática ≤ 10 | EP-001 (estabelecido), todos (aplicado) |
| RNF-MANT-004 | Padronização PEP 8 / Black | EP-001 (estabelecido), todos (aplicado) |

> **Total: 17 RNFs cobertos** (4 RNF-PERF + 4 RNF-USAB + 5 RNF-CONF + 4 RNF-SEG + 4 RNF-MANT, sendo que RNF-SEG-004 é N/A)

---

## Matriz de Rastreabilidade: UC → Épico(s)

| Caso de Uso | Nome | Épicos que Contribuem | Épico onde Fica Completo |
|-------------|------|----------------------|-------------------------|
| UC-001 | Criar e Priorizar Backlog | EP-002, EP-003, EP-004 | EP-008 |
| UC-002 | Alocação Automática com Dependências | EP-005, EP-006, EP-007 | EP-008 |
| UC-003 | Detectar e Resolver Deadlock | EP-005, EP-007 | EP-008 |
| UC-004 | Importar Backlog do Excel | EP-003, EP-004, EP-005 | EP-009 |
| UC-005 | Gerenciar Ondas de Entrega | EP-004 | EP-008 |

---

## Matriz de Rastreabilidade: CT → Épico

| Cenário de Teste | Descrição | Executável Após |
|------------------|-----------|-----------------|
| CT-001 | Backlog Completo 20 Histórias | EP-008 |
| CT-002 | Detecção de Ciclo em Grafo Grande | EP-005 |
| CT-003 | Deadlock por Falta de Devs | EP-007 |
| CT-004 | Feriados em Sequência | EP-006 |
| CT-005 | Balanceamento com Tamanhos Diferentes | EP-007 |

---

## Artefatos Estruturais do SRS → Épico

| Artefato | Seção SRS | Épico |
|----------|-----------|-------|
| Arquitetura em 4 Camadas | §6.1 | EP-001 (estrutura), EP-008 (UI) |
| Fluxo de Alocação Automática | §6.2 | EP-007 |
| Grafo de Dependências | §6.3 | EP-005 |
| Modelo ER (4 tabelas) | §6.4 | EP-001 |
| Máquina de Estados | §6.5 | EP-002 |
| Hierarquia de Exceções | §7.3 | EP-001 |
| Convenções de Nomenclatura | §8.2 | EP-002 |
| Regras Implícitas | §8.3 | EP-002 |
| Feriados Brasileiros | Apêndice A | EP-006 |
| Atalhos de Teclado | Apêndice B | EP-008 |

---

## Resumo por Camada

| Camada | Épicos | RFs | RNFs Principais |
|--------|--------|-----|-----------------|
| Fundação | EP-001 | — | MANT-*, CONF-003/004/005, SEG-001/003 |
| Domínio Core | EP-002, EP-003, EP-004 | 19 | — |
| Serviços de Negócio | EP-005, EP-006, EP-007 | 23 | PERF-001/003 |
| Interface & Experiência | EP-008 | — | USAB-*, PERF-002/004, CONF-001/002 |
| Integração & Otimização | EP-009 | — | SEG-002 |

---

## Notas de Implementação

1. **Ordem é obrigatória**: Nenhum épico deve iniciar antes de suas dependências estarem completas.

2. **RNFs transversais**: RNF-MANT-001 a 004 são estabelecidos em EP-001 e aplicados em todos os épicos subsequentes.

3. **MVP é EP-008**: O produto só é utilizável pelo usuário final após EP-008.

4. **Excel é pós-MVP**: EP-009 adiciona funcionalidade de interoperabilidade, não é requisito para o MVP.

5. **Validação incremental**: Cada épico possui critérios de aceite e plano de validação independentes.

6. **Testes são cumulativos**: A cobertura de testes aumenta a cada épico; CT-001 a CT-005 são executáveis após EP-008.
