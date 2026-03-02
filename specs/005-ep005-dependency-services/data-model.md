# Data Model: EP-005 Gestao de Dependencias - Servicos e Aplicacao

**Date**: 2026-03-01
**Status**: Complete

## Overview

Este epico NAO adiciona novas entidades de dominio ou tabelas de banco de dados.
Implementa apenas:
1. Domain Service (DependencyService) - logica de negocio pura
2. Application Use Cases - coordenacao assincrona
3. DTOs Pydantic - transporte de dados

## Domain Layer

### DependencyService (Domain Service)

Servico de dominio stateless para operacoes com dependencias.
Recebe todos os dados via parametros. Nao acessa repositorios ou faz I/O.

**Constantes para estados do DFS:**
- WHITE = 0 (Nao visitado)
- GRAY = 1 (Em processamento)
- BLACK = 2 (Finalizado)

#### Metodos

| Metodo | Parametros | Retorno | Descricao |
|--------|------------|---------|-----------|
| build_graph | dependencies: Sequence[tuple[str, str]] | dict[str, list[str]] | Constroi grafo de adjacencia |
| would_create_cycle | graph, source, target | list[str] ou None | Verifica se aresta criaria ciclo |
| detect_cycle | graph, source, target | list[str] ou None | DFS iterativo para detectar ciclo |
| validate_wave_dependency | story_wave: int, depends_on_wave: int | bool | True se valido (depends_on <= story) |

### Tipos de Dados

#### Graph Representation

Grafo de adjacencia: story_id -> [depends_on_ids]

Exemplo:
- A depende de B: graph["A"] = ["B"]
- B depende de C: graph["B"] = ["C"]
- Resultado: {"A": ["B"], "B": ["C"], "C": []}

## Application Layer

### DTOs (Data Transfer Objects)

Todos os DTOs herdam de pydantic.BaseModel com validacao automatica.

| DTO | Campos | Descricao |
|-----|--------|-----------|
| AddDependencyInputDTO | story_id: str, depends_on_id: str | Input para adicao |
| AddDependencyOutputDTO | success: bool, story_id: str, depends_on_id: str, warning: WarningDTO ou None | Output com warning opcional |
| InvalidWaveDependencyWarningDTO | story_id, depends_on_id, story_wave, depends_on_wave, message | Warning cross-wave |
| RemoveDependencyInputDTO | story_id: str, depends_on_id: str | Input para remocao |
| RemoveDependencyOutputDTO | success: bool | Output remocao |
| GetDependenciesInputDTO | story_id: str | Input consulta |
| GetDependenciesOutputDTO | story_id: str, dependencies: list[str] | Output dependencias |
| GetDependentsInputDTO | story_id: str | Input consulta |
| GetDependentsOutputDTO | story_id: str, dependents: list[str] | Output dependentes |

### Use Cases

| Use Case | Responsabilidade |
|----------|------------------|
| AddDependencyUseCase | Valida existencia, detecta ciclos, valida waves, persiste |
| RemoveDependencyUseCase | Remove dependencia existente |
| GetDependenciesUseCase | Lista dependencias de uma historia |
| GetDependentsUseCase | Lista dependentes de uma historia |

## Validation Rules

### Invariantes de Entrada

| Campo | Regra | Excecao |
|-------|-------|---------|
| story_id | Nao vazio, trimmed | ValueError |
| depends_on_id | Nao vazio, trimmed | ValueError |
| story_id != depends_on_id | IDs diferentes | ValueError |

### Regras de Negocio

| Regra | Condicao | Acao |
|-------|----------|------|
| Historia existe | story_id deve existir | ValueError |
| Dependencia existe | depends_on_id deve existir | ValueError |
| Sem ciclo | Adicao nao pode criar ciclo | CyclicDependencyException |
| Wave valida | depends_on_wave > story_wave | Warning (nao bloqueia) |
| Dependencia unica | Nao pode duplicar | ValueError |

## Relationships

Tabela Story_Dependency existente (EP-001):
- story_id TEXT NOT NULL
- depends_on_id TEXT NOT NULL
- PRIMARY KEY (story_id, depends_on_id)
- FOREIGN KEY para Story (ON DELETE CASCADE)

## Test Data Patterns

### Grafos de Teste

- dag_simple: A -> B -> C (sem ciclo)
- cycle_direct: A -> B -> A (ciclo direto)
- cycle_indirect: A -> B -> C -> A (ciclo indireto)
- diamond: A -> B,C -> D (multiplos caminhos sem ciclo)
- large_dag: 50 nos em cadeia (performance test)
