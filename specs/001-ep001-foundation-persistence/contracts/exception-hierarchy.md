# Exception Hierarchy: EP-001 Fundacao e Persistencia

**Feature**: EP-001 Fundacao e Persistencia
**Date**: 2026-02-28
**Status**: Completo

## Visao Geral

Este documento define a hierarquia completa de excecoes e warnings do Backlog Manager, conforme FR-014 a FR-024 da especificacao.

---

## Diagrama de Hierarquia

```
Exception (built-in)
├── ValueError  # Usado para validacoes de entidade
│
└── BacklogManagerException  # FR-014: Base customizada
    │
    ├── DependencyException  # FR-015
    │   ├── CyclicDependencyException  # FR-016
    │   └── InvalidWaveDependencyException  # FR-017
    │
    ├── FeatureException  # FR-018
    │   ├── DuplicateWaveException  # FR-019
    │   └── FeatureHasStoriesException  # FR-020
    │
    └── AllocationException  # FR-021
        └── MaxIterationsExceeded  # FR-022

Warning (built-in)
└── BacklogWarning  # FR-023
    ├── DeadlockWarning  # FR-024
    ├── IdlenessWarning  # FR-024
    └── BetweenWavesIdlenessInfo  # FR-024
```

---

## Definicoes Detalhadas

### BacklogManagerException (Base)

```python
class BacklogManagerException(Exception):
    """
    Excecao base para todos os erros do Backlog Manager.

    Todas as excecoes customizadas do sistema herdam desta classe,
    permitindo catch generico para tratamento uniforme de erros.

    Example:
        try:
            # operacao que pode falhar
        except BacklogManagerException as e:
            logger.error("Erro no Backlog Manager: %s", e)
    """
    pass
```

---

### DependencyException

```python
class DependencyException(BacklogManagerException):
    """
    Erros relacionados a dependencias entre historias.

    Classe base para excecoes de ciclo e wave invalida.
    """
    pass
```

### CyclicDependencyException

```python
class CyclicDependencyException(DependencyException):
    """
    Ciclo detectado no grafo de dependencias.

    Lancada quando uma operacao criaria ou detecta um ciclo
    no grafo de dependencias entre historias.

    Attributes:
        path: Lista de IDs de historias formando o ciclo.
              Ex: ["AUTH-001", "AUTH-002", "AUTH-003", "AUTH-001"]

    Example:
        try:
            dependency_service.add_dependency("A", "B")
        except CyclicDependencyException as e:
            print(f"Ciclo detectado: {' -> '.join(e.path)}")
    """

    def __init__(self, path: list[str], message: str | None = None) -> None:
        self.path = path
        cycle_str = " -> ".join(path)
        default_message = f"Ciclo detectado nas dependencias: {cycle_str}"
        super().__init__(message or default_message)
```

### InvalidWaveDependencyException

```python
class InvalidWaveDependencyException(DependencyException):
    """
    Dependencia invalida entre waves.

    Lancada quando uma historia tenta depender de outra
    que pertence a uma wave posterior.

    Attributes:
        story_id: ID da historia que tenta depender.
        depends_on_id: ID da historia da qual tenta depender.
        story_wave: Wave da historia.
        depends_on_wave: Wave da dependencia.

    Example:
        # Historia na wave 1 nao pode depender de historia na wave 2
        raise InvalidWaveDependencyException(
            story_id="AUTH-001",
            depends_on_id="FEAT-001",
            story_wave=1,
            depends_on_wave=2
        )
    """

    def __init__(
        self,
        story_id: str,
        depends_on_id: str,
        story_wave: int,
        depends_on_wave: int,
        message: str | None = None
    ) -> None:
        self.story_id = story_id
        self.depends_on_id = depends_on_id
        self.story_wave = story_wave
        self.depends_on_wave = depends_on_wave
        default_message = (
            f"Historia {story_id} (wave {story_wave}) nao pode depender de "
            f"{depends_on_id} (wave {depends_on_wave}): dependencia de wave posterior"
        )
        super().__init__(message or default_message)
```

---

### FeatureException

```python
class FeatureException(BacklogManagerException):
    """
    Erros relacionados a features.

    Classe base para excecoes de wave duplicada e feature com historias.
    """
    pass
```

### DuplicateWaveException

```python
class DuplicateWaveException(FeatureException):
    """
    Wave duplicada ao criar/atualizar feature.

    Lancada quando tenta-se criar ou atualizar uma feature
    com um numero de wave que ja existe em outra feature.

    Attributes:
        wave: Numero da wave duplicada.
        existing_feature_name: Nome da feature que ja usa a wave.

    Example:
        raise DuplicateWaveException(
            wave=2,
            existing_feature_name="Autenticacao"
        )
    """

    def __init__(
        self,
        wave: int,
        existing_feature_name: str,
        message: str | None = None
    ) -> None:
        self.wave = wave
        self.existing_feature_name = existing_feature_name
        default_message = (
            f"Wave {wave} ja esta em uso pela feature '{existing_feature_name}'"
        )
        super().__init__(message or default_message)
```

### FeatureHasStoriesException

```python
class FeatureHasStoriesException(FeatureException):
    """
    Tentativa de deletar feature com historias associadas.

    Lancada quando tenta-se deletar uma feature que ainda
    possui historias vinculadas.

    Attributes:
        feature_id: ID da feature.
        feature_name: Nome da feature.
        story_count: Numero de historias associadas.

    Example:
        raise FeatureHasStoriesException(
            feature_id=1,
            feature_name="Autenticacao",
            story_count=5
        )
    """

    def __init__(
        self,
        feature_id: int,
        feature_name: str,
        story_count: int,
        message: str | None = None
    ) -> None:
        self.feature_id = feature_id
        self.feature_name = feature_name
        self.story_count = story_count
        default_message = (
            f"Nao e possivel deletar feature '{feature_name}' (ID: {feature_id}): "
            f"existem {story_count} historia(s) associada(s)"
        )
        super().__init__(message or default_message)
```

---

### AllocationException

```python
class AllocationException(BacklogManagerException):
    """
    Erros relacionados a alocacao automatica de historias.

    Classe base para excecoes do algoritmo de alocacao.
    """
    pass
```

### MaxIterationsExceeded

```python
class MaxIterationsExceeded(AllocationException):
    """
    Numero maximo de iteracoes excedido na alocacao.

    Lancada quando o algoritmo de alocacao nao consegue
    convergir dentro do limite de iteracoes.

    Attributes:
        max_iterations: Limite de iteracoes configurado.
        stories_remaining: Numero de historias nao alocadas.

    Example:
        raise MaxIterationsExceeded(
            max_iterations=1000,
            stories_remaining=15
        )
    """

    def __init__(
        self,
        max_iterations: int,
        stories_remaining: int,
        message: str | None = None
    ) -> None:
        self.max_iterations = max_iterations
        self.stories_remaining = stories_remaining
        default_message = (
            f"Alocacao nao convergiu apos {max_iterations} iteracoes: "
            f"{stories_remaining} historia(s) nao alocada(s)"
        )
        super().__init__(message or default_message)
```

---

## Warnings

### BacklogWarning (Base)

```python
import warnings

class BacklogWarning(Warning):
    """
    Warning base para situacoes nao-bloqueantes do Backlog Manager.

    Warnings nao interrompem a execucao, mas sinalizam situacoes
    que merecem atencao do usuario.

    Example:
        warnings.warn(
            "Situacao de atencao",
            BacklogWarning
        )
    """
    pass
```

### DeadlockWarning

```python
class DeadlockWarning(BacklogWarning):
    """
    Deadlock detectado na alocacao de historias.

    Emitido quando o algoritmo de alocacao detecta que nenhum
    progresso e possivel em uma iteracao (todas as historias
    bloqueadas por dependencias ou desenvolvedores ocupados).

    Attributes:
        wave: Wave onde o deadlock foi detectado.
        blocked_stories: Lista de IDs de historias bloqueadas.
    """

    def __init__(
        self,
        wave: int,
        blocked_stories: list[str]
    ) -> None:
        self.wave = wave
        self.blocked_stories = blocked_stories
        message = (
            f"Deadlock detectado na wave {wave}: "
            f"{len(blocked_stories)} historia(s) bloqueada(s)"
        )
        super().__init__(message)
```

### IdlenessWarning

```python
class IdlenessWarning(BacklogWarning):
    """
    Ociosidade detectada para um desenvolvedor.

    Emitido quando um desenvolvedor fica ocioso por mais dias
    do que o configurado em max_idle_days dentro de uma wave.

    Attributes:
        developer_id: ID do desenvolvedor ocioso.
        developer_name: Nome do desenvolvedor.
        idle_days: Numero de dias ociosos.
        wave: Wave onde a ociosidade foi detectada.
    """

    def __init__(
        self,
        developer_id: int,
        developer_name: str,
        idle_days: int,
        wave: int
    ) -> None:
        self.developer_id = developer_id
        self.developer_name = developer_name
        self.idle_days = idle_days
        self.wave = wave
        message = (
            f"Desenvolvedor '{developer_name}' ocioso por {idle_days} dias na wave {wave}"
        )
        super().__init__(message)
```

### BetweenWavesIdlenessInfo

```python
class BetweenWavesIdlenessInfo(BacklogWarning):
    """
    Informativo de ociosidade entre waves.

    Emitido para informar que houve ociosidade na transicao
    entre waves (situacao esperada e nao problematica).

    Attributes:
        developer_id: ID do desenvolvedor.
        developer_name: Nome do desenvolvedor.
        idle_days: Numero de dias ociosos.
        from_wave: Wave de origem.
        to_wave: Wave de destino.
    """

    def __init__(
        self,
        developer_id: int,
        developer_name: str,
        idle_days: int,
        from_wave: int,
        to_wave: int
    ) -> None:
        self.developer_id = developer_id
        self.developer_name = developer_name
        self.idle_days = idle_days
        self.from_wave = from_wave
        self.to_wave = to_wave
        message = (
            f"Desenvolvedor '{developer_name}' ocioso por {idle_days} dias "
            f"entre wave {from_wave} e wave {to_wave} (esperado)"
        )
        super().__init__(message)
```

---

## Uso de Warnings

```python
import warnings
from backlog_manager.domain.exceptions import DeadlockWarning, IdlenessWarning

# Emitir warning
warnings.warn(
    DeadlockWarning(wave=2, blocked_stories=["AUTH-001", "AUTH-002"])
)

# Capturar warnings
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    # ... operacao que pode emitir warnings ...
    for warning in w:
        if issubclass(warning.category, DeadlockWarning):
            logger.warning("Deadlock: %s", warning.message)

# Filtrar warnings especificos
warnings.filterwarnings("ignore", category=BetweenWavesIdlenessInfo)
```

---

## Mapeamento Requisitos -> Implementacao

| Requisito | Classe | Condicao de Disparo |
|-----------|--------|---------------------|
| FR-014 | BacklogManagerException | Base para todas as excecoes |
| FR-015 | DependencyException | Base para erros de dependencia |
| FR-016 | CyclicDependencyException | Ciclo no grafo de dependencias |
| FR-017 | InvalidWaveDependencyException | Dependencia de wave posterior |
| FR-018 | FeatureException | Base para erros de feature |
| FR-019 | DuplicateWaveException | Wave ja existe |
| FR-020 | FeatureHasStoriesException | Deletar feature com historias |
| FR-021 | AllocationException | Base para erros de alocacao |
| FR-022 | MaxIterationsExceeded | Limite de iteracoes atingido |
| FR-023 | BacklogWarning | Base para warnings |
| FR-024 | DeadlockWarning, IdlenessWarning, BetweenWavesIdlenessInfo | Situacoes de alerta |
