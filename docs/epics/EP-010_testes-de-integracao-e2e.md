# EP-010 — Testes de Integracao E2E

**Camada:** Integracao & Otimizacao

---

## Problema que Resolve

Com a implementacao de todas as funcionalidades do Backlog Manager (EP-001 a EP-009), e necessario garantir que os fluxos completos funcionem corretamente de ponta a ponta. Embora cada epico tenha seus proprios testes unitarios e de integracao, nao ha validacao sistematica de que os casos de uso completos (UC-001 a UC-005) e os cenarios de teste do SRS (CT-001 a CT-005) funcionem como esperado quando todas as camadas estao integradas. Este epico implementa uma suite de testes E2E que valida a integridade do sistema como um todo.

## Objetivo (Valor Mensuravel)

Implementar testes de integracao E2E que validem todas as funcionalidades do sistema:
- Cobertura de 100% dos 5 casos de uso do SRS (UC-001 a UC-005)
- Implementacao dos 5 cenarios de teste do SRS (CT-001 a CT-005) como testes automatizados
- Validacao de fluxos completos via pytest-qt com interface grafica
- Garantir cobertura de testes >= 80% (RNF-MANT-001)
- Detectar regressoes antes de releases
- Corrigir bugs revelados pelos testes conforme politica de criticidade

## Alinhamento Estrategico

Este epico valida todas as **7 capacidades** do produto (SRS §2.2):
1. **Gestao de Backlog**: Testada via UC-001 e CT-001
2. **Gestao de Features**: Testada via UC-005
3. **Gestao de Desenvolvedores**: Testada via UC-002
4. **Gestao de Dependencias**: Testada via UC-003 e CT-002
5. **Calculo de Cronograma**: Testado via UC-002 e CT-004
6. **Alocacao Automatica**: Testada via UC-002, CT-003 e CT-005
7. **Integracao Excel**: Testada via UC-004

## Personas Impactadas

| Persona (SRS §2.3) | Impacto |
|--------------------|---------|
| Scrum Master / Tech Lead | Confianca de que os fluxos de planejamento funcionam corretamente |
| Gerente de Projeto | Garantia de confiabilidade do sistema para uso em producao |
| Product Owner | Validacao de que todas as funcionalidades atendem aos requisitos |

## Jornadas / Casos de Uso Afetados

- UC-001: Criar e Priorizar Backlog — Validado por testes E2E
- UC-002: Executar Alocacao Automatica com Dependencias — Validado por testes E2E
- UC-003: Detectar e Resolver Deadlock — Validado por testes E2E
- UC-004: Importar Backlog do Excel — Validado por testes E2E
- UC-005: Gerenciar Ondas de Entrega — Validado por testes E2E
- CT-001 a CT-005: Executaveis apos este epico (testes automatizados)

---

## Escopo

### Dentro do Escopo

**Requisitos Funcionais:**
- Nenhum RF e escopo principal deste epico (epico de qualidade/testes)
- Este epico VALIDA os RFs implementados nos epicos anteriores
- **Correcao de bugs revelados pelos testes E2E** e parte do escopo deste epico

**Requisitos Nao-Funcionais:**
- RNF-MANT-001: Cobertura de testes >= 80% — validacao final
- RNF-CONF-001: Disponibilidade — validar que sessoes completam sem crashes
- RNF-CONF-002: Recuperacao de erros — validar tratamento de erros em fluxos E2E
- RNF-PERF-001: Tempo de alocacao <= 5s para 100 historias — teste de performance
- RNF-PERF-002: Responsividade UI <= 100ms para CRUD — teste de performance

**Artefatos Estruturais do SRS:**
- Casos de Uso (§5): Implementacao como testes automatizados (UC-001 a UC-005)
- Cenarios de Teste (§7.1): Implementacao como testes automatizados (CT-001 a CT-005)
- Matriz de Rastreabilidade (§7.4): Validacao de cobertura RF ↔ CT
- Catalogo de Excecoes (§7.2): Validacao de tratamento de erros

**Politica de Tratamento de Bugs Revelados pelos Testes:**

| Criticidade | Acao Imediata | Documentacao | Acompanhamento |
|-------------|---------------|--------------|----------------|
| **Simples** | Correcao imediata no mesmo PR | Commit message descritivo | Nenhum |
| **Media** | Correcao imediata no mesmo PR | Mapear para analise futura (comentario no codigo ou issue de acompanhamento) | Revisao em retrospectiva |
| **Critica** | Registrar issue detalhada | Identificar causa raiz | Criar plano de acao estruturante para evitar recorrencia |

**Definicao de Criticidade:**
- **Simples**: Bug isolado, causa evidente, correcao pontual (ex: typo, validacao faltante, off-by-one)
- **Media**: Bug que afeta mais de um componente ou tem causa nao-obvia (ex: race condition, estado inconsistente)
- **Critica**: Bug que indica falha arquitetural, de design ou que pode causar perda de dados (ex: corrupcao de banco, crash silencioso, violacao de invariante)

### Fora do Escopo

- Novos RFs ou RNFs → nao serao criados neste epico
- Testes de carga/stress massivos → fora do escopo do produto desktop
- Testes de seguranca penetration testing → fora do escopo
- Cobertura de UI visual 100% → views tem cobertura minima 50% (Constitution XIV)

---

## Requisitos Funcionais Principais

| ID | Nome | Prioridade |
|----|------|------------|
| — | Este epico nao possui RFs como escopo principal | — |

## Requisitos Nao-Funcionais Criticos

| ID | Nome | Metrica-alvo |
|----|------|-------------|
| RNF-MANT-001 | Cobertura de Testes | >= 80% (validacao final) |
| RNF-CONF-001 | Disponibilidade | 99% sessoes sem crash nos testes E2E |
| RNF-CONF-002 | Recuperacao de Erros | 100% erros tratados corretamente |
| RNF-PERF-001 | Tempo de Alocacao | <= 5s para 100 historias |
| RNF-PERF-002 | Responsividade UI | <= 100ms para CRUD |

---

## Criterios de Aceite (Alto Nivel)

### Casos de Uso (UC)
- [ ] **Dado** UC-001 (Criar e Priorizar Backlog), **Quando** executo o teste E2E, **Entao** todas as acoes do fluxo principal sao validadas com sucesso
- [ ] **Dado** UC-002 (Alocacao Automatica), **Quando** executo o teste E2E com dependencias, **Entao** historias sao alocadas respeitando dependencias e ondas
- [ ] **Dado** UC-003 (Detectar Ciclos), **Quando** tento criar dependencia ciclica via UI, **Entao** sistema exibe erro e rejeita a operacao
- [ ] **Dado** UC-004 (Importar Excel), **Quando** importo arquivo valido via UI, **Entao** historias sao criadas e exibidas na lista
- [ ] **Dado** UC-005 (Gerenciar Ondas), **Quando** crio features com ondas via UI, **Entao** historias sao processadas por onda na alocacao

### Cenarios de Teste (CT)
- [ ] **Dado** CT-001 (20 historias, 5 devs), **Quando** executo alocacao, **Entao** tempo < 5s, todas alocadas, distribuicao balanceada
- [ ] **Dado** CT-002 (grafo com 50 nos e ciclo), **Quando** detecto ciclo, **Entao** CyclicDependencyException e lancada em < 100ms
- [ ] **Dado** CT-003 (deadlock por falta de devs), **Quando** aloco, **Entao** data e ajustada sem deadlock
- [ ] **Dado** CT-004 (feriados em sequencia), **Quando** calculo cronograma, **Entao** feriados sao pulados corretamente
- [ ] **Dado** CT-005 (balanceamento desigual), **Quando** aloco, **Entao** distribuicao e por contagem de historias

### Metricas
- [ ] **Dado** suite de testes completa, **Quando** executo pytest-cov, **Entao** cobertura >= 80%
- [ ] **Dado** testes E2E com pytest-qt, **Quando** executo a suite, **Entao** nenhum teste falha por timeout ou crash

### Tratamento de Bugs
- [ ] **Dado** bug simples revelado pelo teste, **Quando** identificado, **Entao** correcao e aplicada imediatamente no mesmo PR
- [ ] **Dado** bug de criticidade media revelado pelo teste, **Quando** identificado, **Entao** correcao e aplicada imediatamente E problema e mapeado para analise futura
- [ ] **Dado** bug critico revelado pelo teste, **Quando** identificado, **Entao** issue e registrada com descricao da causa raiz e plano de acao estruturante e criado

## KPIs / Metricas de Sucesso

| KPI | Metrica | Meta | Fonte SRS |
|-----|---------|------|-----------|
| Cobertura de codigo | % linhas cobertas | >= 80% | RNF-MANT-001 |
| Casos de uso testados | UCs com teste E2E | 5/5 (100%) | §5 |
| Cenarios testados | CTs implementados | 5/5 (100%) | §7.1 |
| Taxa de sucesso | Testes passando | 100% | Qualitativo |
| Tempo de execucao | Suite completa | < 5 minutos | Qualitativo |
| Bugs corrigidos | Bugs revelados e corrigidos | 100% | Qualitativo |
| Bugs criticos documentados | Issues criadas para bugs criticos | 100% | Qualitativo |

## Plano de Validacao

| Tipo | Descricao | Referencia SRS |
|------|-----------|----------------|
| Testes E2E | UC-001: Criar historia, alterar prioridade, editar, deletar | UC-001 |
| Testes E2E | UC-002: Configurar velocidade, calcular datas, alocar automaticamente | UC-002 |
| Testes E2E | UC-003: Adicionar dependencia ciclica, verificar rejeicao | UC-003 |
| Testes E2E | UC-004: Importar Excel valido, verificar criacao de historias | UC-004 |
| Testes E2E | UC-005: Criar features com ondas, validar processamento sequencial | UC-005 |
| Testes E2E | CT-001: Backlog completo com 20 historias e 5 devs | CT-001 |
| Testes E2E | CT-002: Deteccao de ciclo em grafo grande (50 nos) | CT-002 |
| Testes E2E | CT-003: Deadlock por falta de desenvolvedores | CT-003 |
| Testes E2E | CT-004: Feriados em sequencia (Carnaval, Sexta-Santa) | CT-004 |
| Testes E2E | CT-005: Balanceamento com historias de tamanhos diferentes | CT-005 |
| Testes Performance | Tempo de alocacao <= 5s para 100 historias | RNF-PERF-001 |
| Testes Performance | Latencia UI <= 100ms para CRUD | RNF-PERF-002 |
| Revisao de Codigo | Validar uso de pytest-qt com qasync | Constitution XIV |
| Revisao de Codigo | Verificar fixtures qtbot/qeventloop | Constitution XIV |
| Correcao de Bugs | Aplicar correcoes para bugs simples e medios | RNF-CONF-002 |
| Documentacao | Registrar issues para bugs criticos com causa raiz | §7.2 |

---

## Dependencias

| Epico | Motivo |
|-------|--------|
| EP-001 | Infraestrutura de testes (pytest, pytest-cov) e schema do banco |
| EP-002 | Entidades validadas para testes de invariantes |
| EP-003 | StoryService para testar CRUD de historias |
| EP-004 | DeveloperService e FeatureService para testar gestao de recursos |
| EP-005 | DependencyService para testar deteccao de ciclos |
| EP-006 | SchedulingService para testar calculo de cronograma |
| EP-007 | AllocationService para testar alocacao automatica |
| EP-008 | Interface grafica para testes E2E via pytest-qt |
| EP-009 | ExcelService para testar import/export |

## Riscos e Premissas

| Tipo | Descricao | Mitigacao |
|------|-----------|-----------|
| Premissa | pytest-qt e qasync estao configurados corretamente (EP-001/EP-008) | Validar configuracao antes de implementar testes |
| Premissa | Todas as funcionalidades dos epicos anteriores estao implementadas | Executar suite de testes existente antes de iniciar |
| Risco | Testes E2E com GUI podem ser flakey (instabilidade) | Usar qtbot.waitSignal, evitar time.sleep, documentar sincronizacao |
| Risco | Tempo de execucao da suite pode exceder limite aceitavel | Paralelizar testes independentes, usar pytest-xdist se necessario |
| Risco | Cobertura pode nao atingir 80% apenas com testes E2E | Combinar com testes unitarios existentes para meta global |
| Premissa | Ambiente de CI/CD suporta testes com GUI (display virtual) | Configurar xvfb ou similar no pipeline |
| Risco | Mudancas em epicos anteriores podem quebrar testes E2E | Executar testes E2E em CI a cada PR |
| Risco | Bugs criticos podem exigir refatoracao significativa | Isolar correcao em branch separada; priorizar estabilidade sobre features |
| Premissa | Bugs revelados pelos testes serao corrigidos dentro do escopo deste epico | Alocar tempo adicional para correcoes; ajustar estimativas se necessario |
