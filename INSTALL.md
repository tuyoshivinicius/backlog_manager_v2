# Instalação Local — Backlog Manager

Guia para instalar e executar o Backlog Manager a partir do código-fonte.

## Pré-requisitos

- **Python 3.11** ou superior (até 3.14)
- **Poetry** (gerenciador de dependências)

### Instalando o Poetry

Se ainda não tem o Poetry instalado, a forma recomendada é via `pipx`:

```bash
pipx install poetry
```

> Caso não tenha o `pipx`, instale com `pip install --user pipx` e depois `pipx ensurepath`.
>
> Consulte a [documentação oficial do Poetry](https://python-poetry.org/docs/#installation) para métodos alternativos.

## Instalação

1. **Clone o repositório:**

```bash
git clone <url-do-repositorio>
cd backlog_manager_v2
```

2. **Instale as dependências:**

```bash
poetry install --only main
```

Isso cria um ambiente virtual (`.venv`) e instala apenas as dependências de produção.

## Executando

Existem duas formas equivalentes de iniciar a aplicação:

```bash
# Via script registrado
poetry run backlog-manager

# Via módulo Python
poetry run python -m backlog_manager
```

A interface gráfica do Backlog Manager será aberta.

## Nota: Ambiente de Desenvolvimento

Para contribuir com o projeto (testes, linting, formatação), instale todas as dependências:

```bash
poetry install
```

Isso inclui ferramentas como `pytest`, `black`, `ruff`, `mypy`, entre outras.
