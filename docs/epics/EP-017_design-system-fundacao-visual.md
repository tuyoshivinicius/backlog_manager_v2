# EP-017 — Design System e Fundacao Visual (GUI-001)

**Camada:** Interface & Experiencia

---

## Problema que Resolve

A aplicacao implementada em EP-008 nao possui sistema de design: nenhum QSS e aplicado, nao ha tokens de cor/tipografia/espacamento centralizados, nao ha delegates customizados para renderizacao de celulas, e nao ha icones SVG. Toda estilizacao e inconsistente e definida ad-hoc em cada componente. Os requisitos de acessibilidade (RNF-USAB-003: contraste WCAG 4.5:1, navegacao por teclado, tooltips) nao estao implementados de forma sistematica. Sem esta fundacao, cada evolucao futura da UI tera que definir seus proprios valores de cor e estilo, gerando inconsistencia e dificultando manutencao (RNF-MANT-001).

## Objetivo (Valor Mensuravel)

Entregar o modulo de design tokens (`theme.py`), o stylesheet centralizado (`stylesheet.qss`), os delegates de renderizacao customizada (`StatusBadgeDelegate`, `MonospaceDelegate`), a biblioteca de icones SVG, e os padroes de acessibilidade embutidos. Ao final, ao iniciar a aplicacao, **todos os widgets padrao Qt** receberao estilizacao moderna automaticamente via `app.setStyleSheet()`. Os delegates estarao prontos para integracao na tabela.

**Metricas de sucesso:**
- 100% dos widgets recebem estilizacao via QSS centralizado
- Contraste >= 4.5:1 validado para todas as combinacoes texto/fundo (RNF-USAB-003)
- 16 icones SVG disponiveis e carregaveis via QIcon
- Delegates de renderizacao funcionais e testaveis

## Alinhamento Estrategico

Conexao com as capacidades do produto definidas na secao 2.2 do SRS:
- **Capacidade 1 (Gestao de Backlog)**: Tabela de backlog recebera estilizacao moderna e badges de status
- **Capacidade 6 (Alocacao Automatica)**: Painel de metricas sera estilizado consistentemente
- **Transversal**: Fundacao visual habilita todas as 7 capacidades atraves de UI consistente

## Personas Impactadas

| Persona (SRS §2.3) | Impacto |
|--------------------|---------|
| Scrum Master / Tech Lead | Experiencia visual melhorada na interface principal de uso diario |
| Gerente de Projeto | Visualizacao mais clara de status e metricas |
| Product Owner | Interface mais profissional para apresentacao a stakeholders |

## Jornadas / Casos de Uso Afetados

- UC-001: Criar e Priorizar Backlog — contribui para (melhora visual da tabela)
- UC-002: Alocacao Automatica com Dependencias — contribui para (badges de status visiveis)
- CT-001 a CT-005: executaveis com visual melhorado

---

## Escopo

### Dentro do Escopo

**Requisitos Funcionais:**
- Nenhum RF novo — epico de implementacao tecnica para RNFs de usabilidade

**Requisitos Nao-Funcionais:**
- RNF-USAB-003: Acessibilidade basica (contraste 4.5:1, focus ring, areas clicaveis minimas)
- RNF-MANT-001: Manutenibilidade (codigo centralizado, sem valores hardcoded)

**Artefatos Estruturais:**
- Arquitetura em camadas (§6.1): Artefatos na camada Presentation
- Padroes UI/UX (Constitution §XIX): MVVM com delegates

**Componentes a implementar:**

| ID      | Componente                | Tipo  | Descricao |
|---------|---------------------------|-------|-----------|
| DS-001  | Design Tokens (theme.py)  | NOVO  | Modulo Python com constantes de cores (30+ tokens), tipografia, espacamento, border-radius, sombras |
| DS-002  | Stylesheet QSS            | NOVO  | Arquivo QSS centralizado com placeholders `@var`, cobrindo todos os tipos de widget |
| DS-003  | StatusBadgeDelegate       | NOVO  | QStyledItemDelegate para badges pill de status com cores e indicadores nao-cromaticos |
| DS-004  | MonospaceDelegate         | NOVO  | QStyledItemDelegate para IDs em fonte monospace |
| DS-005  | Biblioteca de Icones      | NOVO  | 16 SVGs Phosphor Icons (16x16px) |
| ACC-001 | Contraste WCAG 4.5:1      | NOVO  | Validacao de todas as combinacoes texto/fundo |
| ACC-002 | Indicadores nao-cromaticos| NOVO  | Prefixos de simbolo nos badges de status |
| ACC-003 | Focus ring visivel        | NOVO  | Regras QSS de `:focus` com border @primary |
| ACC-004 | Areas clicaveis minimas   | NOVO  | Dimensoes minimas 32x32px para QToolButton |

### Fora do Escopo

- Integracao dos delegates na tabela → sera tratado em EP-018 (GUI-002)
- Icones aplicados na toolbar/menus → sera tratado em EP-018 (GUI-002)
- Aplicacao de ajustes finos nos dialogs → sera tratado em EP-020 (GUI-005)
- Import/Export Excel → EP-009
- Novos requisitos funcionais

---

## Requisitos Funcionais Principais

| ID | Nome | Prioridade |
|----|------|------------|
| — | Nenhum RF novo — implementacao tecnica de RNFs | — |

## Requisitos Nao-Funcionais Criticos

| ID | Nome | Metrica-alvo |
|----|------|-------------|
| RNF-USAB-003 | Acessibilidade Basica | Contraste >= 4.5:1, focus ring visivel, areas clicaveis 32x32px |
| RNF-MANT-001 | Manutenibilidade | Zero valores hardcoded de cor/fonte fora de theme.py |
| RNF-PERF-002 | Responsividade UI | Renderizacao de delegates <= 16ms por celula (60fps) |

---

## Criterios de Aceite (Alto Nivel)

### Design Tokens
- [ ] **Dado** aplicacao iniciada, **Quando** inspeciono widgets, **Entao** todos recebem estilizacao do QSS centralizado
- [ ] **Dado** theme.py, **Quando** verifico constantes, **Entao** contem 30+ tokens de cor, 6 tamanhos de fonte, 7 espacamentos, 4 border-radius, 3 sombras

### Stylesheet QSS
- [ ] **Dado** stylesheet.qss, **Quando** verifico conteudo, **Entao** cobre QMainWindow, QToolBar, QToolButton, QTableView, QHeaderView, QDialog, QPushButton, QLineEdit, QComboBox, QSpinBox, QDateEdit, QStatusBar, QMenuBar, QMenu, QScrollBar
- [ ] **Dado** stylesheet.qss, **Quando** verifico valores, **Entao** usa apenas placeholders `@var` (nenhum hex literal)

### Delegates
- [ ] **Dado** StatusBadgeDelegate, **Quando** renderiza status BACKLOG, **Entao** exibe pill com prefixo "●" e cores corretas
- [ ] **Dado** StatusBadgeDelegate, **Quando** renderiza status CONCLUIDO, **Entao** exibe pill com prefixo "✓" e cores corretas
- [ ] **Dado** MonospaceDelegate, **Quando** renderiza ID, **Entao** usa fonte JetBrains Mono ou fallback Consolas

### Acessibilidade
- [ ] **Dado** combinacao texto/fundo de badge, **Quando** calculo contraste, **Entao** ratio >= 4.5:1 (WCAG AA)
- [ ] **Dado** navegacao por Tab, **Quando** foco em widget interativo, **Entao** focus ring visivel (border 2px solid @primary)
- [ ] **Dado** QToolButton, **Quando** verifico dimensoes, **Entao** minimo 32x32px

### Icones
- [ ] **Dado** 16 arquivos SVG em assets/icons/, **Quando** carrego via QIcon, **Entao** renderizam corretamente em 16x16px

## KPIs / Metricas de Sucesso

| KPI | Metrica | Meta | Fonte SRS |
|-----|---------|------|-----------|
| Cobertura de widgets | % de tipos de widget estilizados | 100% | RNF-USAB-003 |
| Contraste minimo | Ratio WCAG | >= 4.5:1 | RNF-USAB-003 |
| Valores centralizados | Hardcoded colors fora de theme.py | 0 | RNF-MANT-001 |
| Performance de delegate | Tempo de renderizacao por celula | <= 16ms | RNF-PERF-002 |

## Plano de Validacao

| Tipo | Descricao | Referencia SRS |
|------|-----------|----------------|
| Teste Manual | Iniciar aplicacao e verificar que widgets recebem estilizacao do QSS | RNF-USAB-003 |
| Teste Manual | Inspecionar visualmente que icones SVG carregam sem distorcao | RNF-USAB-003 |
| Teste Unitario | Testar `apply_theme()`: dado template com placeholders, retorna QSS com valores substituidos | RNF-MANT-001 |
| Teste Unitario | Testar `StatusBadgeDelegate.paint()`: renderiza corretamente para cada status (mock QPainter) | RNF-USAB-003 |
| Teste Unitario | Testar `MonospaceDelegate`: aplica familia de fonte monospace | RNF-USAB-003 |
| Revisao de Codigo | Verificar que nenhum valor hardcoded de cor/fonte aparece fora de theme.py | RNF-MANT-001 |
| Revisao de Codigo | Confirmar que QSS usa exclusivamente placeholders @var | RNF-MANT-001 |
| Teste de Contraste | Validar ratio >= 4.5:1 para todas as combinacoes listadas | RNF-USAB-003 |

---

## Dependencias

| Epico | Motivo |
|-------|--------|
| EP-008 | Interface grafica basica implementada — GUI-001 refatora e estiliza a UI existente |

## Riscos e Premissas

| Tipo | Descricao | Mitigacao |
|------|-----------|-----------|
| Risco | QSS do PySide6 pode nao suportar todas as propriedades CSS (ex: outline, opacity) | Testar cada propriedade isoladamente. Usar alternativas (border ao inves de outline, alpha no color ao inves de opacity) |
| Risco | Fontes Inter/JetBrains Mono podem nao estar instaladas no Windows do usuario | Usar fallback chain nativa: "Inter", "Segoe UI", system-ui e "JetBrains Mono", "Cascadia Code", "Consolas" |
| Risco | SVGs Phosphor podem ter problemas de renderizacao via QIcon em certas resolucoes | Validar renderizacao em 100% e 125% DPI. Usar QSvgRenderer se QIcon nao funcionar |
| Risco | apply_theme() com replace sequencial pode ter conflitos de substituicao | Ordenar substituicoes do mais longo para o mais curto (ex: @primary-pressed antes de @primary) |
| Premissa | PySide6 6.6.1+ suporta QSS suficiente para estilizacao moderna | Conforme SRS §2.4 |
| Premissa | Segoe UI e Consolas estao disponiveis em todas as instalacoes Windows 10/11 | Fontes nativas do Windows |

---

## Especificacoes Tecnicas (Referencia)

### Arquivos a Criar/Editar

| Arquivo | Acao | Descricao |
|---------|------|-----------|
| `src/backlog_manager/presentation/styles/__init__.py` | CRIAR | Tornar styles/ um pacote Python |
| `src/backlog_manager/presentation/styles/theme.py` | CRIAR | Modulo de design tokens com 30+ constantes e apply_theme() |
| `src/backlog_manager/presentation/styles/stylesheet.qss` | CRIAR | Stylesheet QSS centralizado |
| `src/backlog_manager/presentation/delegates/__init__.py` | CRIAR | Tornar delegates/ um pacote Python |
| `src/backlog_manager/presentation/delegates/status_badge_delegate.py` | CRIAR | QStyledItemDelegate para badges |
| `src/backlog_manager/presentation/delegates/monospace_delegate.py` | CRIAR | QStyledItemDelegate para IDs |
| `src/backlog_manager/presentation/assets/icons/` | CRIAR | Diretorio com 16 arquivos SVG |
| `src/backlog_manager/presentation/app.py` | EDITAR | Carregar stylesheet.qss e aplicar apply_theme() |

### Paleta de Cores (theme.py)

```python
# Cores primarias
PRIMARY = "#5B5BD6"        # indigo - acoes, selecao, links
PRIMARY_HOVER = "#4C4CC4"
PRIMARY_PRESSED = "#3E3EB0"
PRIMARY_LIGHT = "#EEF2FF"  # fundo de selecao

# Semanticas
SUCCESS = "#30A46C"        # verde - conclusao
WARNING = "#F5A623"        # ambar - atencao
ERROR = "#E5484D"          # vermelho - impedido/destrutivo

# Neutras (13 tons)
NEUTRAL_0 = "#FFFFFF"      # fundo de dialogs
NEUTRAL_50 = "#FAFAFA"     # fundo do MainWindow
# ... (demais conforme GUI-001)

# Badges de status
STATUS_COLORS = {
    "BACKLOG":   {"bg": "#E5E5E5", "text": "#525252", "border": "#D4D4D4"},
    "EXECUCAO":  {"bg": "#EEF2FF", "text": "#5B5BD6", "border": "#C7D2FE"},
    "TESTES":    {"bg": "#FFF7C2", "text": "#946800", "border": "#F5D90A"},
    "CONCLUIDO": {"bg": "#DDF3E4", "text": "#18794E", "border": "#8ECEAA"},
    "IMPEDIDO":  {"bg": "#FFE5E5", "text": "#CE2C31", "border": "#F9A8AB"},
}

# Indicadores nao-cromaticos
STATUS_SYMBOLS = {
    "BACKLOG": "●", "EXECUCAO": "▶", "TESTES": "◆",
    "CONCLUIDO": "✓", "IMPEDIDO": "✕",
}
```

### Icones SVG (16 arquivos)

| Arquivo | Uso | Tamanho |
|---------|-----|---------|
| plus.svg | + Nova | 16x16px |
| pencil-simple.svg | Editar | 16x16px |
| trash.svg | Deletar | 16x16px |
| arrow-up.svg | Mover Cima | 16x16px |
| arrow-down.svg | Mover Baixo | 16x16px |
| users.svg | Desenvolvedores | 16x16px |
| package.svg | Features | 16x16px |
| gear.svg | Configuracao | 16x16px |
| calendar-check.svg | Calcular Cronograma | 16x16px |
| shuffle.svg | Alocar Devs | 16x16px |
| download-simple.svg | Importar | 16x16px |
| upload-simple.svg | Exportar | 16x16px |
| copy.svg | Duplicar | 16x16px |
| warning-triangle.svg | Alerta | 16x16px |
| link.svg | Dependencias | 16x16px |
| x.svg | Fechar | 16x16px |
