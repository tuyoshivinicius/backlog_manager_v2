# Research: Script de Seed para Teste de Alocação

**Date**: 2026-03-12
**Feature**: EP-014 Script de Seed para Teste de Alocação

## 1. Geração de Dependências sem Ciclos

### Decisão
Usar topological ordering para garantir dependências acíclicas: histórias são geradas em ordem de wave e prioridade, e dependências só podem apontar para histórias já criadas (índice menor no array).

### Rationale
- Ordem topológica garante DAG (Directed Acyclic Graph) por construção
- Histórias de wave N só podem depender de histórias de waves 1..N
- Intra-onda: histórias com prioridade menor (mais prioritárias) podem ser dependências
- Simple e determinístico com random seed fixo

### Alternativas Consideradas
1. **Geração aleatória com validação de ciclo**: Gera dependência aleatória e valida com DFS. Rejeitado: overhead desnecessário, pode ter muitas rejeições
2. **Matriz de adjacência pré-calculada**: Gera matriz válida primeiro. Rejeitado: complexidade desnecessária para este caso
3. **Kahn's algorithm para ordenação**: Rejeitado: resolve o problema inverso (dado grafo, ordena), não gera grafo

## 2. Reutilização do init_database

### Decisão
Importar e chamar `init_database(db_path)` da infraestrutura existente antes de popular dados.

### Rationale
- Reutiliza schema.sql centralizado (conforme FR-015)
- Garante consistência com aplicação principal
- Evita duplicação de código de schema
- Já tratado para criar diretórios se necessário

### Implementação
```python
from backlog_manager.infrastructure.database.sqlite_connection import (
    init_database,
    create_connection,
)

async def seed_database(db_path: Path | None = None) -> None:
    await init_database(db_path)
    conn = await create_connection(db_path)
    # ... popular dados
```

## 3. Argumentos CLI

### Decisão
Usar `argparse` (stdlib) com dois argumentos opcionais: `--clean` e `--db-path`.

### Rationale
- argparse é standard library, sem dependências adicionais
- Suficiente para 2 argumentos simples
- Suporta help automático (`-h`)

### Alternativas Consideradas
1. **click**: Mais ergonômico para CLIs complexas. Rejeitado: overkill para 2 argumentos, adiciona dependência
2. **typer**: Modern e type-safe. Rejeitado: adiciona dependência
3. **sys.argv manual**: Rejeitado: não tem help automático, propenso a bugs

### Interface CLI
```
usage: seed_test_backlog.py [-h] [--clean] [--db-path PATH]

Seed test backlog for allocation engine testing.

options:
  -h, --help       show this help message and exit
  --clean          Remove existing data before seeding
  --db-path PATH   Custom database path (default: app default)
```

## 4. Estrutura de Dados de Seed

### Decisão
Definir dados como constantes no script com estrutura:
- `DEVELOPERS`: lista de 7 nomes
- `WAVES`: dict wave -> (domain, components[])
- Story points distribuídos por peso: 3 (30%), 5 (35%), 8 (25%), 13 (10%)

### Rationale
- Dados fixos garantem reproducibilidade (SC-004)
- Estrutura por wave facilita geração de features e histórias
- Distribuição de SP realista conforme SC-007

### Estrutura
```python
DEVELOPERS = ["Ana", "Bruno", "Carlos", "Diana", "Eduardo", "Fernanda", "Gabriel"]

WAVES = {
    1: ("Autenticação", ["AUTH"]),
    2: ("Usuários", ["USER"]),
    3: ("Produtos", ["PROD"]),
    4: ("Carrinho", ["CART"]),
    5: ("Pagamentos", ["PAY"]),
    6: ("Relatórios", ["REPORT"]),
    7: ("Notificações e API", ["NOTIF", "API"]),
}

SP_WEIGHTS = [(3, 30), (5, 35), (8, 25), (13, 10)]  # (valor, peso%)
```

## 5. Transação Atômica

### Decisão
Usar context manager `async with conn` para transação implícita, com `await conn.commit()` ao final e rollback automático em exceção.

### Rationale
- aiosqlite suporta context manager para transação
- Rollback automático garante estado consistente em erro
- Conforme FR-011

### Implementação
```python
async with conn:
    try:
        # todas as inserções
        await conn.commit()
    except Exception:
        await conn.rollback()
        raise
```

## 6. Log de Progresso

### Decisão
Usar `logging.getLogger(__name__)` com mensagens INFO para cada etapa e resumo final.

### Rationale
- Conforme Princípio XVII da constituição
- Mensagens em português conforme requisito
- INFO level suficiente para progresso

### Mensagens
- "Iniciando seed do backlog de teste..."
- "Criados {n} desenvolvedores"
- "Criadas {n} features em {w} ondas"
- "Criadas {n} histórias"
- "Criadas {n} dependências"
- "Seed concluído com sucesso!"

## 7. Verificação de Dados Existentes

### Decisão
Sem `--clean`: verificar se tabelas têm dados e falhar com mensagem informativa.
Com `--clean`: deletar dados na ordem correta (Story_Dependency -> Story -> Feature -> Developer).

### Rationale
- Protege contra sobrescrita acidental de dados
- Ordem de deleção respeita foreign keys
- Conforme FR-007 e acceptance scenario US3

### Implementação
```python
async def check_existing_data(conn: aiosqlite.Connection) -> bool:
    result = await conn.execute("SELECT COUNT(*) FROM Story")
    count = (await result.fetchone())[0]
    return count > 0

async def clean_data(conn: aiosqlite.Connection) -> None:
    await conn.execute("DELETE FROM Story_Dependency")
    await conn.execute("DELETE FROM Story")
    await conn.execute("DELETE FROM Feature")
    await conn.execute("DELETE FROM Developer")
```
