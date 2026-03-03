# Research: EP-005 Gestao de Dependencias - Servicos e Aplicacao

**Date**: 2026-03-01
**Status**: Complete

## Research Tasks

### 1. Algoritmo DFS para Deteccao de Ciclos

**Objetivo**: Determinar a melhor abordagem para deteccao de ciclos em grafos direcionados.

**Pesquisa**:
- DFS (Depth-First Search) e o algoritmo padrao para deteccao de ciclos em grafos direcionados
- Abordagem classica usa coloracao de nos: WHITE (nao visitado), GRAY (em processamento), BLACK (finalizado)
- Ciclo e detectado quando encontramos uma aresta para um no GRAY (back edge)
- Complexidade: O(V+E) onde V = vertices e E = arestas

**Decisao**: Implementar DFS iterativo com pilha explicita (evita stack overflow em Python)

**Rationale**:
- Python tem limite de recursao (~1000 por default)
- Backlog pode ter 500+ historias com muitas dependencias
- DFS iterativo garante mesma complexidade sem risco de stack overflow

**Alternativas Consideradas**:
1. DFS recursivo - Descartado: risco de stack overflow
2. BFS (Kahn's algorithm) - Descartado: detecta ciclo mas nao fornece o caminho do ciclo facilmente
3. Tarjan's algorithm - Descartado: overengineering para o caso de uso

### 2. Construcao do Caminho do Ciclo

**Objetivo**: Determinar como construir o caminho exato do ciclo para feedback ao usuario.

**Pesquisa**:
- O spec exige formato ["A", "B", "C", "A"] onde primeiro e ultimo sao iguais
- Durante DFS, precisamos manter um mapa de "parent" para reconstruir o caminho
- Quando detectamos back edge para no GRAY, tracamos o caminho de volta

**Decisao**: Manter dicionario `parent: dict[str, str]` durante DFS

**Rationale**:
- Permite reconstruir caminho em O(path_length)
- Memoria adicional O(V) aceitavel para escala do projeto

**Implementacao**:
```python
def build_cycle_path(parent: dict[str, str], start: str, end: str) -> list[str]:
    """Constroi caminho do ciclo de start ate end, incluindo back edge."""
    path = [end]
    current = start
    while current != end:
        path.append(current)
        current = parent[current]
    path.append(end)  # Fechar ciclo
    return list(reversed(path))
```

### 3. Validacao de Wave (Cross-Wave Dependency)

**Objetivo**: Definir regra de negocio para warning de dependencia entre waves.

**Pesquisa**:
- Wave e derivada da Feature associada a historia
- Historia sem feature tem wave=0 (implicitamente "pre-wave 1")
- Dependencia "invalida" e quando story.wave < depends_on.wave
  - Ex: Historia em wave 1 depende de historia em wave 2 = warning

**Decisao**: Warning (nao bloqueante) quando `story_wave < depends_on_wave`

**Rationale**:
- Permite flexibilidade ao usuario
- Warning e informativo, nao impede a operacao
- Retornado no DTO de output para que UI possa exibir

**Casos Especiais**:
- wave=0 (sem feature) < wave=1 -> warning
- wave=0 depende de wave=0 -> OK (sem warning)
- wave=2 depende de wave=1 -> OK (sem warning)
- wave=1 depende de wave=2 -> WARNING

### 4. Integracao com Repositorios Existentes

**Objetivo**: Verificar APIs disponiveis nos repositorios.

**Pesquisa no Codigo**:

| Metodo | Repositorio | Status | Uso no EP-005 |
|--------|-------------|--------|---------------|
| `exists(story_id)` | StoryRepository | ✅ Existe | Validar existencia antes de adicionar dependencia |
| `get_by_id(feature_id)` | FeatureRepository | ✅ Existe | Obter wave da feature |
| `add(story_id, depends_on_id)` | StoryDependencyRepository | ✅ Existe | Persistir dependencia |
| `remove(story_id, depends_on_id)` | StoryDependencyRepository | ✅ Existe | Remover dependencia |
| `get_dependencies(story_id)` | StoryDependencyRepository | ✅ Existe | Listar dependencias |
| `get_dependents(story_id)` | StoryDependencyRepository | ✅ Existe | Listar dependentes |
| `get_all_dependencies()` | StoryDependencyRepository | ✅ Existe | Construir grafo completo |
| `exists(story_id, depends_on_id)` | StoryDependencyRepository | ✅ Existe | Verificar se dependencia existe |

**Decisao**: Todos os metodos necessarios ja existem. Nao e necessario modificar repositorios.

### 5. Padrao de Use Cases Existentes

**Objetivo**: Garantir consistencia com use cases ja implementados.

**Pesquisa no Codigo** (EP-003, EP-004):
- Use cases recebem `UnitOfWork` via construtor
- Metodo principal e `async def execute(input_dto) -> output_dto`
- Usa context manager do UnitOfWork para transacoes
- DTOs sao Pydantic BaseModel

**Decisao**: Seguir mesmo padrao

**Exemplo de Referencia** (`delete_story.py`):
```python
class DeleteStoryUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, story_id: str) -> None:
        # Validacoes
        # Operacoes
        pass
```

### 6. Excecoes de Dominio Existentes

**Objetivo**: Verificar excecoes ja definidas.

**Pesquisa** (`domain/exceptions/dependency.py`):
- `CyclicDependencyException(path: list[str])` - ✅ Existe
- `InvalidWaveDependencyException(story_id, depends_on_id, story_wave, depends_on_wave)` - ✅ Existe

**Decisao**: Reutilizar excecoes existentes sem modificacoes.

### 7. Performance: Benchmark de Referencia

**Objetivo**: Validar meta de performance CT-002 (< 100ms para 50 nos).

**Analise**:
- DFS iterativo O(V+E) com V=50, E~100 = ~150 operacoes
- Python executa ~1M operacoes/segundo conservadoramente
- Estimativa: ~0.15ms para 50 nos, muito abaixo de 100ms

**Decisao**: Performance nao e preocupacao. Implementacao padrao atende requisito.

**Validacao**: Criar teste de performance para validar empiricamente.

## Summary de Decisoes

| Topico | Decisao | Justificativa |
|--------|---------|---------------|
| Algoritmo | DFS iterativo com pilha | Evita stack overflow |
| Estados | WHITE/GRAY/BLACK | Padrao classico |
| Caminho ciclo | Dicionario parent | O(V) memoria, O(path) construcao |
| Wave warning | `story_wave < depends_on_wave` | Nao bloqueante, informativo |
| Repositorios | Reutilizar existentes | Todas APIs disponiveis |
| Use Case pattern | UnitOfWork + async execute | Consistencia com EP-003/004 |
| Excecoes | Reutilizar existentes | Ja definidas corretamente |
| Performance | Implementacao padrao | Meta facilmente atingivel |

## Proximos Passos

Com todas as questoes de pesquisa resolvidas, prosseguir para Phase 1:
1. Definir data-model.md
2. Criar contracts/ (se aplicavel)
3. Criar quickstart.md
