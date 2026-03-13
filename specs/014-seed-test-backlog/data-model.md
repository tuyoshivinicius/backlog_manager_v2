# Data Model: Script de Seed para Teste de Alocação

**Date**: 2026-03-12
**Feature**: EP-014 Script de Seed para Teste de Alocação

## Entidades Existentes (Reutilizadas)

Este script utiliza as entidades já definidas no schema.sql do projeto. Não cria novas entidades.

### Developer

| Campo | Tipo | Constraints | Descrição |
|-------|------|-------------|-----------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Identificador único |
| name | VARCHAR(100) | NOT NULL | Nome do desenvolvedor |

**Dados Gerados**: 7 desenvolvedores com nomes fixos.

### Feature

| Campo | Tipo | Constraints | Descrição |
|-------|------|-------------|-----------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Identificador único |
| name | VARCHAR(100) | NOT NULL UNIQUE | Nome da feature |
| wave | INTEGER | NOT NULL UNIQUE, > 0 | Número da onda |

**Dados Gerados**: ~30 features distribuídas em 7 ondas (4-5 por onda).

### Story

| Campo | Tipo | Constraints | Descrição |
|-------|------|-------------|-----------|
| id | VARCHAR(20) | PRIMARY KEY | Formato COMPONENTE-NNN |
| component | VARCHAR(50) | NOT NULL | Componente/módulo |
| name | VARCHAR(200) | NOT NULL | Nome da história |
| story_points | INTEGER | NOT NULL, IN (3,5,8,13) | Estimativa Fibonacci |
| priority | INTEGER | NOT NULL, >= 0 | Prioridade (menor = mais prioritário) |
| status | VARCHAR(20) | NOT NULL DEFAULT 'BACKLOG' | Estado do workflow |
| duration | INTEGER | NULL | Duração calculada |
| start_date | DATE | NULL | Data início (não preenchida no seed) |
| end_date | DATE | NULL | Data término (não preenchida no seed) |
| developer_id | INTEGER | FK Developer(id) NULL | Não alocado no seed |
| feature_id | INTEGER | FK Feature(id) NULL | Feature associada |

**Dados Gerados**: 150-200 histórias com status BACKLOG, sem alocação.

### Story_Dependency

| Campo | Tipo | Constraints | Descrição |
|-------|------|-------------|-----------|
| story_id | VARCHAR(20) | FK Story(id), NOT NULL | História dependente |
| depends_on_id | VARCHAR(20) | FK Story(id), NOT NULL | Pré-requisito |

**Constraints Compostos**:
- PRIMARY KEY (story_id, depends_on_id)
- CHECK (story_id != depends_on_id)

**Dados Gerados**: 80-120 dependências (60% intra-onda, 40% inter-onda).

## Constantes de Seed

### Desenvolvedores

```python
DEVELOPERS = [
    "Ana",
    "Bruno",
    "Carlos",
    "Diana",
    "Eduardo",
    "Fernanda",
    "Gabriel",
]
```

### Ondas e Componentes

| Wave | Domínio | Componentes | Features (~4-5) |
|------|---------|-------------|-----------------|
| 1 | Autenticação | AUTH | Login, Registro, Recuperação Senha, OAuth, 2FA |
| 2 | Usuários | USER | Perfil, Preferências, Avatar, Endereços |
| 3 | Produtos | PROD | Catálogo, Busca, Detalhes, Favoritos, Comparação |
| 4 | Carrinho | CART | Adicionar, Remover, Atualizar, Cupons |
| 5 | Pagamentos | PAY | Checkout, Cartão, Pix, Boleto, Histórico |
| 6 | Relatórios | REPORT | Dashboard, Vendas, Usuários, Produtos |
| 7 | Comunicação | NOTIF, API | Push, Email, Webhooks, REST, GraphQL |

### Distribuição de Story Points

| SP | Peso | Histórias (~180 total) |
|----|------|------------------------|
| 3 | 30% | ~54 |
| 5 | 35% | ~63 |
| 8 | 25% | ~45 |
| 13 | 10% | ~18 |

### Distribuição de Dependências

| Tipo | Proporção | Quantidade (~100 total) |
|------|-----------|-------------------------|
| Intra-onda | 60% | ~60 |
| Inter-onda | 40% | ~40 |

## Regras de Geração de Dependências

1. **Ordem topológica garantida**: História A só pode depender de história B se:
   - wave(B) < wave(A), OU
   - wave(B) == wave(A) E priority(B) < priority(A)

2. **Sem auto-dependência**: story_id != depends_on_id (garantido pelo CHECK)

3. **Sem ciclos**: Garantido pela regra de ordem topológica

4. **Máximo de dependências por história**: 3 (evita grafo muito denso)

5. **Distribuição por onda**:
   - Onda 1: sem dependências (raiz do grafo)
   - Ondas 2-7: mix de intra e inter-onda

## Formato de ID de História

```
COMPONENTE-NNN
```

Onde:
- COMPONENTE: código do componente (AUTH, USER, PROD, CART, PAY, REPORT, NOTIF, API)
- NNN: número sequencial com zero-padding (001, 002, ...)

Exemplos:
- AUTH-001, AUTH-002, ..., AUTH-025
- USER-001, USER-002, ..., USER-030
- PROD-001, PROD-002, ..., PROD-035

## Cenários Críticos Incluídos (FR-014)

1. **Cadeia longa de dependências**: AUTH-001 → USER-010 → PROD-020 → CART-015 → PAY-005
2. **Histórias com múltiplas dependências**: REPORT-001 depende de USER-005, PROD-010, PAY-003
3. **Ondas com densidades variadas**: Onda 3 (PROD) mais densa, Onda 6 (REPORT) menos densa
