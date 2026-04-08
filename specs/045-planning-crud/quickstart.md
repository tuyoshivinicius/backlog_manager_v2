# Quickstart: Modulo de Planejamentos

**Feature**: 045-planning-crud | **Date**: 2026-04-08

## Pre-requisitos

- Python 3.11+
- Poetry instalado
- Dependencias do projeto instaladas (`poetry install`)

## Executando a aplicacao

```bash
poetry run python -m backlog_manager
```

## Fluxo basico — Primeiro uso

1. Ao iniciar pela primeira vez, o sistema solicita a criacao de um planejamento
2. Informe o nome (ex: "Sprint 45") e confirme
3. Cadastre historias normalmente — todas serao associadas ao planejamento ativo
4. O titulo da janela exibe o nome do planejamento ativo

## Fluxo basico — Multiplos planejamentos

1. **Criar**: Menu `Arquivo > Novo Planejamento` (Ctrl+N) → informa nome → planejamento criado e ativado
2. **Abrir**: Menu `Arquivo > Abrir Planejamento` (Ctrl+O) → seleciona da lista → historias carregadas
3. **Editar**: Dentro do dialogo "Abrir Planejamento", botao de editar ao lado do item → renomeia inline
4. **Excluir**: Dentro do dialogo "Abrir Planejamento", botao de excluir ao lado do item → confirmacao → remove com historias

## Fluxo basico — Reiniciar planejamento

1. Menu `Ferramentas > Reiniciar Planejamento` → limpa campos calculados (datas, dev, duracao) das historias do planejamento ativo
2. Nao confundir com "Novo Planejamento" que cria um planejamento

## Executando testes

```bash
# Todos os testes
poetry run pytest

# Testes unitarios da entidade Planning
poetry run pytest tests/unit/domain/test_planning.py -v

# Testes unitarios dos use cases de Planning
poetry run pytest tests/unit/application/test_planning_use_cases.py -v

# Testes de integracao do repositorio
poetry run pytest tests/integration/infrastructure/test_planning_repository.py -v
```

## Migracao de dados

Se o banco de dados ja possui historias sem planejamento (schema antigo), a migracao eh executada automaticamente no startup:
- Cria o planejamento "Planejamento Inicial"
- Associa todas as historias existentes a ele
- Nenhuma acao manual necessaria

## Arquivos-chave

| Arquivo | Descricao |
|---------|-----------|
| `src/backlog_manager/domain/entities/planning.py` | Entidade de dominio Planning |
| `src/backlog_manager/domain/interfaces/repositories.py` | Protocol PlanningRepository |
| `src/backlog_manager/application/use_cases/planning/` | Use cases CRUD |
| `src/backlog_manager/infrastructure/database/repositories/planning_repository.py` | Implementacao SQLite |
| `src/backlog_manager/infrastructure/database/schema.sql` | Schema com tabela Planning |
| `src/backlog_manager/presentation/views/open_planning_dialog.py` | Dialogo "Abrir Planejamento" |
| `src/backlog_manager/presentation/views/create_planning_dialog.py` | Dialogo "Novo Planejamento" |
| `src/backlog_manager/presentation/viewmodels/planning_viewmodel.py` | ViewModel de planejamentos |
