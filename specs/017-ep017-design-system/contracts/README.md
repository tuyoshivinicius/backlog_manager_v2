# Contracts: EP-017 Design System e Fundacao Visual

**Status**: N/A - Este epic nao expoe interfaces externas

## Overview

O EP-017 Design System e um epic puramente interno da camada Presentation. Nao expoe:
- APIs REST/GraphQL
- Comandos CLI
- Protocolos de comunicacao
- Interfaces publicas para bibliotecas externas

## Internal Interfaces

As unicas interfaces publicas sao para consumo interno da aplicacao:

### 1. apply_theme(qss_template: str, tokens: dict[str, str]) -> str

**Purpose**: Substitui placeholders @var em template QSS por valores de tokens.

**Usage**:
```python
from backlog_manager.presentation.theme import apply_theme, DESIGN_TOKENS

stylesheet = apply_theme(qss_content, DESIGN_TOKENS)
app.setStyleSheet(stylesheet)
```

### 2. IconManager.get(name: str) -> QIcon

**Purpose**: Retorna icone SVG pre-carregado pelo nome.

**Usage**:
```python
from backlog_manager.presentation.theme import icon_manager

action = QAction(icon_manager.get("plus"), "Nova Historia", self)
```

### 3. StatusBadgeDelegate / MonospaceDelegate

**Purpose**: Custom delegates para renderizacao de celulas em QTableView.

**Usage**:
```python
from backlog_manager.presentation.delegates import StatusBadgeDelegate, MonospaceDelegate

table.setItemDelegateForColumn(STATUS_COLUMN, StatusBadgeDelegate())
table.setItemDelegateForColumn(ID_COLUMN, MonospaceDelegate())
```

## Why No External Contracts

1. **Escopo do Epic**: Design system e infraestrutura visual interna
2. **Consumidores**: Apenas codigo da propria aplicacao (views, viewmodels)
3. **Estabilidade**: Interfaces internas podem evoluir sem versionamento formal
4. **Clean Architecture**: Presentation layer nao expoe interfaces para camadas externas
