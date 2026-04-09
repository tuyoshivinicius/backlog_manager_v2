# Instalação Local — Backlog Manager

Guia para instalar e executar o Backlog Manager a partir do código-fonte.

## Pré-requisitos

- **Python 3.13** ou superior (até 3.14)

## Instalação Rápida (pip)

Método recomendado para uso local — não requer Poetry instalado.

1. **Clone o repositório:**

```bash
git clone <url-do-repositorio>
cd backlog_manager_v2
```

2. **Execute o instalador (Windows):**

```bash
INSTALL.bat
```

Isso cria um ambiente virtual (`.venv`) e instala o pacote via `pip install .`.

3. **Execute a aplicação:**

```bash
RUN.bat
```

### Instalação manual (pip)

```bash
python -m venv .venv
.venv\Scripts\pip install .
.venv\Scripts\zion-backlog-manager.exe
```

## Instalação via Poetry (desenvolvimento/CI)

Para contribuir com o projeto (testes, linting, formatação), use Poetry:

1. **Instale o Poetry** (se não tiver):

```bash
pipx install poetry
```

2. **Instale todas as dependências:**

```bash
poetry install            # Desenvolvimento (inclui pytest, ruff, mypy, etc.)
poetry install --only main  # Apenas produção
```

3. **Execute a aplicação:**

```bash
poetry run zion-backlog-manager
# OU
poetry run python -m backlog_manager
```
