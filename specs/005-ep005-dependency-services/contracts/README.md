# Contracts: EP-005 Dependency Services

**Date**: 2026-03-01
**Status**: Complete

## Overview

Este epico implementa componentes internos da biblioteca (domain service e use cases).
NAO expoe interfaces publicas externas (CLI, API REST, etc.).

## Internal Python Contracts

Os contratos internos sao definidos como:
1. **Type Hints** - Assinaturas de metodos com tipos
2. **Protocols** - Interfaces abstratas (ja existentes em domain/interfaces/)
3. **DTOs Pydantic** - Contratos de dados validados

### DependencyService Contract

Metodos estaticos para logica de negocio:
- build_graph(dependencies) -> dict[str, list[str]]
- would_create_cycle(graph, source, target) -> list[str] | None
- validate_wave_dependency(story_wave, depends_on_wave) -> bool

### Use Case Contracts

Todos use cases seguem o padrao:
- Construtor recebe UnitOfWork
- Metodo async execute(input_dto) -> output_dto

### DTO Contracts

Ver data-model.md para especificacao completa dos DTOs.

## External Contracts

Nenhum contrato externo e definido neste epico (biblioteca interna).
