# Research: README Profissional do Projeto

**Feature**: 038-readme-profissional
**Date**: 2026-04-02

## R-001: Estrutura de README Profissional para Projetos Open Source

**Decision**: Seguir a estrutura recomendada por projetos enterprise open source com: badges no topo, introdução concisa, TOC, seções de conceito/filosofia, funcionalidades, instalação, uso, arquitetura, stack, contribuição e licença.

**Rationale**: Projetos maduros (FastAPI, Poetry, Pydantic) seguem padrão similar. Badges no topo transmitem profissionalismo imediato. TOC com âncoras facilita navegação em READMEs longos.

**Alternatives considered**:
- README minimalista (apenas instalação + uso) — rejeitado por não atender SC-005 (nível enterprise)
- Wiki separada — rejeitado por fragmentar informação essencial e reduzir discoverability

## R-002: Badges Enterprise — Serviços e Formato

**Decision**: Manter todos os 10 badges existentes (CI, Codecov, SonarCloud Quality Gate, Maintainability, Reliability, Security, PyPI version, PyPI downloads, Python versions, License). Usar shields.io como provedor padrão. Organizar em linhas agrupadas por categoria.

**Rationale**: Os badges já existem no README atual e cobrem todos os requisitos do FR-002. shields.io é o padrão de facto para badges em projetos open source.

**Alternatives considered**:
- Badgen.net — menor ecossistema, sem vantagem clara
- Badges customizados — manutenção desnecessária

## R-003: Diagrama de Arquitetura em ASCII

**Decision**: Usar diagrama ASCII estilo box-drawing representando as 4 camadas da Clean Architecture (Presentation → Infrastructure → Application → Domain) com tecnologias associadas. Baseado no diagrama já presente na constitution.md.

**Rationale**: ASCII art é universalmente renderizável (texto plano e markdown). O diagrama da constitution já modela as camadas corretamente.

**Alternatives considered**:
- Mermaid diagrams — nem todos os renderizadores GitHub mobile suportam bem; ASCII é mais portável
- Imagem PNG — requer manutenção de asset externo, não é editável inline

## R-004: Screenshot da Aplicação

**Decision**: O README deve referenciar um screenshot da interface principal (`docs/images/screenshot.png`). O screenshot será um placeholder até ser capturado manualmente.

**Rationale**: FR-015 exige screenshot. Como a aplicação requer ambiente gráfico (PySide6/Qt), o screenshot deve ser capturado manualmente no ambiente do desenvolvedor.

**Alternatives considered**:
- Screenshot automatizado via CI — complexidade alta para ambiente Qt headless, não justificável

## R-005: Existência do Arquivo LICENSE

**Decision**: O repositório NÃO possui arquivo LICENSE na raiz. O README deve referenciar a licença MIT conforme declarada no pyproject.toml, mas a criação do arquivo LICENSE está FORA do escopo desta feature (requer issue separada).

**Rationale**: O badge de licença já aponta para o GitHub que infere do pyproject.toml. A criação do LICENSE é uma tarefa separada.

**Alternatives considered**:
- Criar LICENSE nesta feature — foge do escopo de documentação README

## R-006: Versão Python Suportada

**Decision**: O README deve informar Python `>=3.13,<3.15` conforme pyproject.toml. O edge case de usuários com versão inferior deve ser coberto na seção de pré-requisitos.

**Rationale**: pyproject.toml define `python = ">=3.13,<3.15"` como constraint.

**Alternatives considered**: N/A — a versão é definida pelo projeto.

## R-007: Nome do Pacote e Comando de Execução

**Decision**: O pacote PyPI se chama `zion-backlog-manager`. O comando de execução é `zion-backlog-manager` (definido em `[tool.poetry.scripts]`).

**Rationale**: Informação extraída diretamente do pyproject.toml.

**Alternatives considered**: N/A.
