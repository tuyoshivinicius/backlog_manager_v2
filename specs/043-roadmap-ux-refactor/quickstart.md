# Quickstart: Roadmap UX Refactor

**Feature**: 043-roadmap-ux-refactor | **Date**: 2026-04-05

## Pre-requisitos

```bash
# Ambiente virtual ativo com dependencias instaladas
poetry install
```

## Executar Testes

```bash
# Testes do ViewModel (headless — sem Qt)
python -m pytest tests/unit/presentation/viewmodels/test_roadmap_viewmodel.py -v

# Testes da View (headless — sem Qt)
python -m pytest tests/unit/presentation/views/test_roadmap_dialog.py -v

# Todos os testes da presentation layer
python -m pytest tests/unit/presentation/ -v

# Com coverage
python -m pytest tests/unit/presentation/ --cov=src/backlog_manager/presentation --cov-report=term-missing
```

## Verificacao Visual (manual)

```bash
# Executar a aplicacao
poetry run backlog-manager
```

1. Abrir o roadmap (Ctrl+Shift+R ou menu)
2. Verificar funcionalidades existentes:
   - Grupos por feature (nao por wave)
   - Expand/collapse com click no cabecalho
   - Codigo da historia nas barras (ex: AUTH-001)
   - Metricas no cabecalho: "Feature Name — N historias | X%"
   - Toolbar organizada: Zoom | Filtros | Dependencias | Fechar
   - Filtros: feature, componente, responsavel, busca por nome
   - Zoom in/out/reset funcionando
   - Toggle de dependencias
   - Scroll vertical com multiplas features expandidas

3. Verificar pan/drag (novas funcionalidades):
   - Cursor de mao aberta ao passar sobre area do grafico
   - Aplicar zoom (Ctrl+Scroll ou botoes) para ampliar
   - Click+arrastar no grafico: viewport desloca horizontalmente
   - Cursor muda para mao fechada durante arrasto
   - Soltar botao: cursor volta para mao aberta
   - Click sem arrastar: toggle de grupo continua funcionando
   - Teclas de seta esquerda/direita: desloca viewport 10%
   - Botao "Ajustar tela": reseta zoom E posicao de pan
   - Arrastar ate limite: conteudo nao desaparece completamente

## Arquivos Modificados

| Arquivo | Descricao |
|---------|-----------|
| `src/backlog_manager/presentation/viewmodels/roadmap_viewmodel.py` | Agrupamento por feature, filtros, metricas |
| `src/backlog_manager/presentation/views/roadmap_dialog.py` | Toolbar, barras com codigo, sidebar, filtros |
| `tests/unit/presentation/viewmodels/test_roadmap_viewmodel.py` | Testes do ViewModel |
| `tests/unit/presentation/views/test_roadmap_dialog.py` | Testes da View |

## Metas de Coverage

| Modulo | Meta |
|--------|------|
| presentation/viewmodels | 90%+ |
| presentation/views | 50%+ |
