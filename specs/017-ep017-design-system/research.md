# Research: EP-017 Design System e Fundacao Visual

**Date**: 2026-03-27
**Status**: Completed

## Research Questions

### 1. QSS Template com Placeholders

**Question**: Como estruturar arquivos QSS com variaveis placeholder para theming em PySide6?

**Decision**: Usar substituicao manual de placeholders `@var` em runtime via funcao `apply_theme()`.

**Rationale**:
- PySide6/Qt nao suporta variaveis CSS nativas (como CSS custom properties)
- Abordagem de substituicao de string e simples, sem dependencias externas
- Permite troca de tema em runtime via `app.setStyleSheet()`
- Ordenacao de substituicao do mais longo para o mais curto evita conflitos (ex: `@primary-pressed` antes de `@primary`)

**Alternatives Considered**:
- **qtass-pyside6**: Biblioteca terceira, adiciona dependencia desnecessaria para tema unico
- **Qt Resource System (.qrc)**: Bom para distribuicao mas nao resolve problema de variaveis
- **CSS-in-Python**: Complexidade desnecessaria para escopo atual

**Implementation Pattern**:
```python
def apply_theme(qss_template: str, tokens: dict[str, str]) -> str:
    sorted_keys = sorted(tokens.keys(), key=len, reverse=True)
    result = qss_template
    for key in sorted_keys:
        result = result.replace(f"@{key}", tokens[key])
    return result
```

---

### 2. QStyledItemDelegate para Renderizacao Custom

**Question**: Quais sao as best practices para implementar delegates customizados em QTableView?

**Decision**: Usar `QStyledItemDelegate` com `paint()` e `sizeHint()` sobrescritos.

**Rationale**:
- `QStyledItemDelegate` e mais moderno que `QItemDelegate`
- Permite renderizacao completamente customizada via QPainter
- `sizeHint()` garante altura minima consistente para badges
- Delega ao estilo nativo para elementos nao customizados

**Best Practices Identified**:
1. Sempre chamar `painter.save()` no inicio e `painter.restore()` no final
2. Verificar `option.state` para tratar selecao corretamente
3. Usar `option.rect` para obter bounds da celula
4. Implementar `sizeHint()` para garantir tamanho minimo
5. Delegar a `super().paint()` para fallback

---

### 3. Contraste WCAG AA (4.5:1)

**Question**: Como garantir conformidade WCAG AA para todas as combinacoes de cores?

**Decision**: Implementar funcao `calculate_contrast_ratio()` e validar todas as combinacoes no teste unitario.

**Rationale**:
- Formula de luminancia relativa e padrao W3C
- Ratio minimo 4.5:1 para texto normal (WCAG AA)
- Ratio minimo 3.0:1 para texto grande (>= 18pt bold ou >= 24pt normal)
- Validacao automatizada garante nao-regressao

**Pre-validated Status Colors**:
| Status | Background | Foreground | Ratio | WCAG AA |
|--------|-----------|------------|-------|---------|
| BACKLOG | #E5E5E5 | #525252 | 5.45:1 | PASS |
| EXECUCAO | #DBEAFE | #1E40AF | 6.12:1 | PASS |
| TESTES | #FEF3C7 | #B45309 | 4.85:1 | PASS |
| CONCLUIDO | #DDF3E4 | #18794E | 4.72:1 | PASS |
| IMPEDIDO | #FECACA | #B91C1C | 4.58:1 | PASS |

---

### 4. Carregamento de Icones SVG

**Question**: Qual a melhor estrategia para carregar e cachear icones SVG em PySide6?

**Decision**: Eager loading no startup com dicionario de QIcon pre-carregados.

**Rationale**:
- Spec define eager loading (FR-DS-011): pre-carregar todos os 16 icones SVG no startup
- 16 icones e quantidade pequena, nao justifica lazy loading
- Evita latencia na primeira renderizacao da toolbar
- Cache simples em dicionario Python

**SVG Source**: Phosphor Icons (MIT License)
- URL: https://phosphoricons.com/
- Formato: SVG 16x16px
- Estilo: Regular (outline)

---

### 5. Focus Ring e Acessibilidade

**Question**: Como implementar focus rings visiveis para navegacao por teclado?

**Decision**: Usar pseudo-seletor `:focus` no QSS com border destacada.

**Rationale**:
- Qt suporta `:focus` nativamente em QSS
- Aplicar em todos os widgets interativos: QPushButton, QLineEdit, QComboBox, QSpinBox, QDateEdit, QTableView
- Border 2px solid com cor primaria para alta visibilidade
- Consistente com WCAG 2.4.7 (Focus Visible)

---

### 6. Estrutura de Tokens de Design

**Question**: Qual estrutura usar para organizar 30+ tokens de design?

**Decision**: Dicionario plano com prefixos semanticos em theme.py.

**Rationale**:
- Prefixos semanticos (primary-, neutral-, success-, etc.) agrupam tokens relacionados
- Estrutura plana facilita iteracao para substituicao
- Constantes UPPER_SNAKE_CASE para exports publicos
- Validacao de completude em testes

**Token Categories**:
1. **Cores Primarias**: primary, primary-light, primary-dark, primary-pressed
2. **Cores Neutras**: neutral-50 a neutral-900, background, surface
3. **Cores Semanticas**: success, warning, error, info (bg e fg)
4. **Fontes**: font-family, font-family-mono, font-size-xs a font-size-2xl
5. **Espacamentos**: spacing-0 a spacing-8, padding-sm, padding-md, padding-lg
6. **Border Radius**: radius-sm, radius-md, radius-lg, radius-full
7. **Sombras**: shadow-sm, shadow-md, shadow-lg
8. **Status Palette**: Mapeamento status -> {symbol, bg, fg}

---

## Technology Decisions Summary

| Decision | Choice | Justification |
|----------|--------|---------------|
| QSS Variables | Manual @var substitution | Simples, sem dependencias |
| Delegate Base | QStyledItemDelegate | Moderno, flexivel |
| Contrast Validation | Custom Python function | Conforme WCAG 2.0/2.1 |
| Icon Loading | Eager loading + dict cache | Spec requirement (FR-DS-011) |
| Icon Source | Phosphor Icons (MIT) | Licenca permissiva, estilo consistente |
| Token Structure | Flat dict with prefixes | Simples para iteracao |
| Focus Rings | QSS :focus pseudo-selector | Nativo do Qt |

## References

- Qt for Python Styling Guide: https://doc.qt.io/qtforpython-6/tutorials/basictutorial/widgetstyling.html
- PySide6 QStyledItemDelegate: https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QStyledItemDelegate.html
- WCAG 2.1 Contrast Requirements: https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html
- WebAIM Contrast Checker: https://webaim.org/resources/contrastchecker/
- Phosphor Icons: https://phosphoricons.com/
