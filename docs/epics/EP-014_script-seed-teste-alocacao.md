# EP-014 — Script de Seed para Teste de Alocacao

**Camada:** Integracao & Otimizacao

---

## Problema que Resolve

Para validar o motor de alocacao automatica (EP-007) e o calculo de cronograma (EP-006) em cenarios reais e complexos, e necessario ter um conjunto de dados de teste representativo. Criar manualmente 150-200 historias com dependencias intra-onda e inter-ondas e impraticavel. Este epico fornece um script de seed que popula o banco de dados com um backlog simulado de projeto real, permitindo testar:
- Processamento de multiplas ondas (7 ondas)
- Dependencias dentro da mesma onda
- Dependencias entre ondas (onda maior depende de onda menor)
- Balanceamento de carga entre 7 desenvolvedores
- Deteccao de deadlocks e ociosidade
- Performance com volume realista de dados

## Objetivo (Valor Mensuravel)

Criar script de seed que:
- Insere 7 desenvolvedores com nomes realistas
- Cria ~30 features distribuidas em 7 ondas (4-5 features/onda)
- Gera ~150-200 historias com story points variados (3, 5, 8, 13)
- Estabelece dependencias intra-onda (dentro da mesma onda)
- Estabelece dependencias inter-ondas (historias de ondas maiores dependem de ondas menores)
- Garante ausencia de ciclos de dependencia
- Executa em menos de 5 segundos

## Alinhamento Estrategico

Este epico suporta diretamente as **capacidades 5 e 6** do produto:
- **Capacidade 5** (Calculo de Cronograma): Permite testar ordenacao topologica e calculo de datas com volume realista
- **Capacidade 6** (Alocacao Automatica): Permite testar balanceamento, deteccao de deadlock e metricas

## Personas Impactadas

| Persona (SRS §2.3) | Impacto |
|--------------------|---------|
| Scrum Master / Tech Lead | Usa seed para validar cenarios de alocacao antes de usar em producao |
| Gerente de Projeto | Testa visualizacao de cronograma com dados realistas |
| Product Owner | Valida comportamento do sistema com backlog volumoso |

## Jornadas / Casos de Uso Afetados

- UC-002: Alocacao Automatica com Dependencias — Habilita testes end-to-end
- CT-001: Backlog Completo 20 Historias — Seed fornece cenario expandido (150+ historias)
- CT-003: Deadlock por Falta de Desenvolvedores — Seed cria cenarios propicios
- CT-005: Balanceamento com Tamanhos Diferentes — Seed inclui historias de tamanhos variados

---

## Escopo

### Dentro do Escopo

**Script de Seed:**
- Arquivo `scripts/seed_test_backlog.py` na raiz do projeto
- Funcao principal `seed_database(db_path: str | None = None)`
- Limpa dados existentes antes de inserir (opcional via flag)
- Gera dados deterministicos (seed de random fixo para reproducibilidade)
- Log de progresso durante execucao

**Dados Gerados:**

| Entidade | Quantidade | Caracteristicas |
|----------|------------|-----------------|
| Developer | 7 | Ana, Bruno, Carlos, Diana, Eduardo, Fernanda, Gabriel |
| Feature | ~30 | 4-5 por onda, nomes realistas por dominio (Auth, Payment, Reports, etc.) |
| Story | ~150-200 | Distribuidas entre features, SP variados, prioridades sequenciais |
| Story_Dependency | ~80-120 | Mix intra-onda (60%) e inter-ondas (40%) |

**Cenarios Criticos Incluidos:**
- Cadeia de dependencias longa (A→B→C→D→E) cruzando ondas
- Historia com multiplas dependencias (prerequisitos)
- Ondas com alta densidade de dependencias internas
- Ondas com poucas historias (teste de ociosidade)
- Ondas com muitas historias (teste de carga)

**Regras de Dependencia:**
- Historia de onda N pode depender de historia de onda M onde M < N
- Historia de onda N pode depender de historia de onda N (intra-onda)
- Historia de onda N NAO pode depender de historia de onda M onde M > N
- Nenhum ciclo de dependencia (validado antes de inserir)

**Requisitos Nao-Funcionais:**
- RNF-PERF-001: Seed executa em < 5 segundos
- RNF-CONF-003: Usa transacoes para garantir consistencia (ACID)

### Fora do Escopo

- Interface grafica para executar seed → executar via CLI
- Configuracao dinamica de quantidade de ondas/features → valores hardcoded
- Dados de teste para cenarios de erro/excecao → epico de testes (EP-010)

---

## Requisitos Funcionais Principais

| ID | Nome | Prioridade |
|----|------|------------|
| RF-SEED-001 | Inserir Desenvolvedores | Must Have |
| RF-SEED-002 | Inserir Features por Onda | Must Have |
| RF-SEED-003 | Gerar Historias com SP Variados | Must Have |
| RF-SEED-004 | Criar Dependencias Intra-Onda | Must Have |
| RF-SEED-005 | Criar Dependencias Inter-Ondas | Must Have |
| RF-SEED-006 | Validar Ausencia de Ciclos | Must Have |
| RF-SEED-007 | Limpar Dados Existentes (opcional) | Should Have |
| RF-SEED-008 | Log de Progresso | Should Have |

## Requisitos Nao-Funcionais Criticos

| ID | Nome | Metrica-alvo |
|----|------|-------------|
| RNF-PERF-001 | Tempo de Execucao | < 5 segundos |
| RNF-CONF-003 | Integridade de Dados | Transacao atomica |
| RNF-MANT-001 | Cobertura de Testes | Conforme EP-001 |

---

## Criterios de Aceite (Alto Nivel)

### Desenvolvedores
- [ ] **Dado** banco vazio, **Quando** executo seed, **Entao** 7 desenvolvedores sao criados com nomes: Ana, Bruno, Carlos, Diana, Eduardo, Fernanda, Gabriel

### Features e Ondas
- [ ] **Dado** banco vazio, **Quando** executo seed, **Entao** ~30 features sao criadas distribuidas em 7 ondas
- [ ] **Dado** onda 1, **Quando** verifico features, **Entao** existem 4-5 features com wave=1

### Historias
- [ ] **Dado** banco vazio, **Quando** executo seed, **Entao** 150-200 historias sao criadas
- [ ] **Dado** historias criadas, **Quando** verifico story_points, **Entao** valores sao 3, 5, 8 ou 13
- [ ] **Dado** historias criadas, **Quando** verifico IDs, **Entao** formato e COMPONENTE-NNN

### Dependencias
- [ ] **Dado** historia em onda 5, **Quando** verifico dependencias, **Entao** dependencias estao em ondas <= 5
- [ ] **Dado** todas as dependencias, **Quando** executo deteccao de ciclos, **Entao** nenhum ciclo e encontrado
- [ ] **Dado** dependencias criadas, **Quando** conto total, **Entao** ~80-120 dependencias existem

### Performance
- [ ] **Dado** banco vazio, **Quando** executo seed completo, **Entao** tempo total < 5 segundos

### Limpeza
- [ ] **Dado** banco com dados existentes, **Quando** executo seed com flag --clean, **Entao** dados anteriores sao removidos antes de inserir

## KPIs / Metricas de Sucesso

| KPI | Metrica | Meta | Fonte SRS |
|-----|---------|------|-----------|
| Tempo de seed | Segundos | < 5s | RNF-PERF-001 |
| Historias geradas | Contagem | 150-200 | - |
| Dependencias validas | % sem ciclos | 100% | RF-DEP-003 |
| Ondas cobertas | Quantidade | 7 | RF-ALOC-006 |

## Plano de Validacao

| Tipo | Descricao | Referencia SRS |
|------|-----------|----------------|
| Teste de Integracao | Executar seed e verificar contagens | - |
| Teste de Integracao | Verificar ausencia de ciclos pos-seed | RF-DEP-003 |
| Teste de Performance | Medir tempo de execucao | RNF-PERF-001 |
| Teste Manual | Executar alocacao automatica apos seed | RF-ALOC-001 |
| Teste Manual | Verificar metricas de alocacao | RF-ALOC-011 |

---

## Dependencias

| Epico | Motivo |
|-------|--------|
| EP-001 | Infraestrutura de banco de dados e schema SQLite |
| EP-002 | Entidades Story, Developer, Feature |
| EP-003 | StoryRepository para verificar consistencia |
| EP-005 | DependencyService para validar ciclos |

## Riscos e Premissas

| Tipo | Descricao | Mitigacao |
|------|-----------|-----------|
| Premissa | Schema do banco esta estavel (nao muda durante desenvolvimento) | Seed usa INSERT direto, nao entidades |
| Premissa | 7 ondas e suficiente para testar cenarios criticos | Pode ser expandido em versao futura |
| Risco | Seed pode criar dados inconsistentes se executado parcialmente | Usar transacao atomica (BEGIN/COMMIT) |
| Risco | Dependencias aleatorias podem criar ciclos | Validar antes de inserir; usar algoritmo DFS |
| Premissa | Random seed fixo (42) garante reproducibilidade | Documentar seed usado |

---

## Especificacao Tecnica do Script

### Estrutura de Dados

```python
DEVELOPERS = [
    "Ana", "Bruno", "Carlos", "Diana",
    "Eduardo", "Fernanda", "Gabriel"
]

WAVES_CONFIG = {
    1: ["Auth", "Core", "Database", "Config"],
    2: ["User", "Profile", "Settings", "Permissions"],
    3: ["Products", "Inventory", "Categories", "Search"],
    4: ["Cart", "Checkout", "Payment", "Orders"],
    5: ["Reports", "Analytics", "Dashboard", "Metrics"],
    6: ["Notifications", "Email", "SMS", "Push"],
    7: ["Integration", "API", "Webhooks", "Export"],
}

COMPONENTS = ["AUTH", "USER", "PROD", "CART", "PAY", "REPORT", "NOTIF", "API"]
```

### Algoritmo de Geracao de Dependencias

1. Para cada historia H em onda W:
   - 30% de chance de ter dependencia intra-onda
   - 40% de chance de ter dependencia inter-ondas (para W > 1)
   - 30% sem dependencias
2. Selecionar dependencia:
   - Intra-onda: escolher historia aleatoria da mesma onda com prioridade menor
   - Inter-ondas: escolher historia aleatoria de onda anterior
3. Validar ciclo antes de adicionar
4. Limitar a 3 dependencias por historia

### Execucao

```bash
# Via CLI
python scripts/seed_test_backlog.py

# Com limpeza
python scripts/seed_test_backlog.py --clean

# Com path customizado
python scripts/seed_test_backlog.py --db-path ./test.db
```
