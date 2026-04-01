# Data Model: Cobertura de Testes 90% e Quality Gate SonarQube

**Feature**: 036-test-coverage-90 | **Date**: 2026-04-01

## Visão Geral

Esta feature **não introduz novas entidades, modifica schema SQLite ou altera modelos de dados**. O escopo é exclusivamente:

1. Configuração de exclusões de cobertura (arquivo de propriedades)
2. Adição de testes unitários e de integração (arquivos de teste)

## Artefatos de Configuração

### sonar-project.properties

**Alteração**: Expandir `sonar.coverage.exclusions` para alinhar com `[tool.coverage.run].omit` do `pyproject.toml`.

```properties
# ANTES
sonar.coverage.exclusions=**/tests/**,**/conftest.py

# DEPOIS
sonar.coverage.exclusions=**/tests/**,**/conftest.py,**/__init__.py,**/presentation/app.py,**/presentation/views/**,**/presentation/delegates/**,**/__main__.py,**/domain/interfaces/**,**/presentation/constants.py
```

**Impacto estimado**: Cobertura SonarQube sobe de 56.7% para ~94%.

## Entidades Existentes Relevantes (somente leitura)

Os testes interagem com as seguintes entidades de domínio **sem modificá-las**:

| Entidade | Localização | Uso nos Testes |
|---|---|---|
| `Story` | `domain/entities/story.py` | Fixture/factory para testar use cases e viewmodels |
| `Developer` | `domain/entities/developer.py` | Fixture/factory para testar alocação |
| `Feature` | `domain/entities/feature.py` | Fixture/factory para testar dependências |
| `Configuration` | `domain/entities/configuration.py` | Fixture para testar scheduling |

## DTOs Existentes Relevantes (somente leitura)

| DTO | Localização | Uso nos Testes |
|---|---|---|
| `StoryDTO` | `application/dto/story/story_dto.py` | Input/output de use cases de story |
| `EditStoryDTO` | `application/dto/story/edit_story_dto.py` | Alvo de testes (cobertura 69.8%) |
| `DeveloperDTO` | `application/dto/developer_dto.py` | Input/output de use cases de developer |
| `AllocationResultDTO` | `application/dto/allocation_result_dto.py` | Output de execute_allocation |

## Interfaces/Protocols Relevantes (somente leitura)

| Interface | Localização | Uso nos Testes |
|---|---|---|
| `StoryRepository` | `domain/interfaces/repositories.py` | Mockado em testes de use cases |
| `DeveloperRepository` | `domain/interfaces/repositories.py` | Mockado em testes de use cases |
| `FeatureRepository` | `domain/interfaces/repositories.py` | Mockado em testes de use cases |
| `UnitOfWork` | `infrastructure/database/unit_of_work.py` | Mockado em testes de use cases |

## State Transitions

Não aplicável — esta feature não altera estados de entidades.

## Validação

Não aplicável — esta feature não introduz novas regras de validação. Os testes validam regras existentes.
