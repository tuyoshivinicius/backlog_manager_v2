# Quickstart: README Profissional do Projeto

**Feature**: 038-readme-profissional
**Date**: 2026-04-02

## Pré-requisitos

- Acesso ao repositório `tuyoshivinicius/zion-backlog-manager` no GitHub
- Conhecimento básico de Markdown/GitHub Flavored Markdown
- Informações dos serviços de badges (CI, Codecov, SonarCloud, PyPI) — já configurados

## Passos para Implementação

### 1. Escrever o README.md

Reescrever o arquivo `README.md` na raiz do repositório seguindo a estrutura definida em `data-model.md`. O conteúdo atual (apenas badges) será substituído integralmente.

### 2. Validar Renderização

```bash
# Verificar no GitHub (push para branch e visualizar)
git push origin 038-readme-profissional

# Ou usar ferramenta local de preview
# pip install grip
# grip README.md
```

### 3. Validar Badges

Verificar que todos os 10 badges renderizam corretamente acessando a branch no GitHub:
- CI status → link para Actions
- Codecov → link para dashboard de cobertura
- SonarCloud (Quality Gate, Maintainability, Reliability, Security) → links para SonarCloud
- PyPI (version, downloads, Python versions) → links para PyPI
- License → link para LICENSE/repositório

### 4. Validar Links e Âncoras

- Todos os links do TOC devem navegar para a seção correspondente
- Links externos (PyPI, GitHub, SonarCloud) devem abrir corretamente

### 5. Screenshot (Opcional nesta fase)

- Capturar screenshot da interface principal da aplicação
- Salvar em `docs/images/screenshot.png`
- Referenciar no README

## Critérios de Aceitação

- [ ] README renderiza corretamente no GitHub
- [ ] Todos os badges aparecem e linkam corretamente
- [ ] TOC com âncoras funcionais
- [ ] Instruções de instalação (pip e Poetry) claras e testáveis
- [ ] Diagrama ASCII de arquitetura visível
- [ ] Conteúdo 100% em português brasileiro
