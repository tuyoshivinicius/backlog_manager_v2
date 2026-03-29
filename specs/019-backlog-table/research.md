# Research: EP-019 — Tabela de Backlog (GUI-003)

**Date**: 2026-03-29 | **Branch**: `019-backlog-table`

## R-001: Estrategia de Enriquecimento do DTO

**Contexto**: O `StoryOutputDTO` atual contem apenas `developer_id: int | None` e `feature_id: int | None`, sem nomes resolvidos. A tabela precisa exibir developer_name, feature_name, wave, e dependencies formatadas.

**Decision**: Enriquecer o DTO na camada Application, dentro do `ListStoriesUseCase`, seguindo o padrao ja estabelecido pelo `ExportExcelUseCase`.

**Rationale**:
- O `ExportExcelUseCase` (linhas 71-77 e 131-142) ja implementa exatamente esse padrao: constroi lookup maps de developers e features, resolve nomes e formata dependencias.
- Manter a resolucao no use case respeita Clean Architecture (Principio I) — Presentation nunca acessa repositorios.
- O `UnitOfWork` ja expoe `developers`, `features` e `dependencies` como repositorios.
- Adicionar campos opcionais ao DTO (com defaults) mantem backward compatibility com outros use cases que nao enriquecem.

**Alternatives considered**:
- ViewModel resolver nomes via dados auxiliares injetados: Viola MVVM puro e Clean Architecture (Presentation acessando dados de infraestrutura indiretamente). Rejeitado.
- Criar um DTO separado `EnrichedStoryOutputDTO`: Duplicacao desnecessaria. O Pydantic BaseModel aceita campos opcionais com default. Rejeitado.

**Implementation approach**:
1. Adicionar campos opcionais ao `StoryOutputDTO`:
   - `developer_name: str | None = None`
   - `feature_name: str | None = None`
   - `wave: int = 0`
   - `dependency_ids: list[str] = Field(default_factory=list)`
2. No `ListStoriesUseCase.execute()`, construir lookup maps e enriquecer:
   ```python
   developers = await self._uow.developers.get_all()
   features = await self._uow.features.get_all()
   dev_map = {d.id: d.name for d in developers if d.id is not None}
   feat_map: dict[int, tuple[str, int]] = {
       f.id: (f.name, f.wave) for f in features if f.id is not None
   }
   ```
3. Manter `from_entity()` inalterado — enriquecimento acontece apos conversao.

---

## R-002: Reposicionamento de Delegates nos Novos Indices

**Contexto**: Atualmente, `MonospaceDelegate` esta na coluna 0 (ID) e `StatusBadgeDelegate` na coluna 3 (Status). Com a expansao para 13 colunas e reordenacao, os indices mudam.

**Decision**: Mapear delegates para os novos indices: ID → coluna 3, Status → coluna 6.

**Rationale**:
- Nova ordem de colunas: Prioridade(0), Feature(1), Onda(2), ID(3), Componente(4), Nome(5), Status(6), Desenvolvedor(7), Dependencias(8), SP(9), Inicio(10), Fim(11), Duracao(12).
- O `main_window.py` atualmente busca "Status" dinamicamente pelo header text (linhas 300-307) — esse padrao e robusto e continuara funcionando.
- O `MonospaceDelegate` esta hardcoded na coluna 0 (linha 297) — precisa ser atualizado para coluna 3, ou tambem usar busca dinamica.

**Alternatives considered**:
- Manter busca por indice hardcoded: Fragil se colunas mudarem novamente. Rejeitado parcialmente — usar busca dinamica para ambos delegates.
- Configurar delegate mapping no ViewModel: Over-engineering para 2 delegates. Rejeitado.

**Implementation approach**:
- Usar busca dinamica por header text para ambos delegates ("ID" e "Status").
- Fallback: se header nao encontrado, log warning e nao aplica delegate.

---

## R-003: Padrao de Estado Vazio

**Contexto**: Quando nao ha historias, a tabela deve exibir mensagem orientativa centralizada e desabilitar botoes "Calcular Cronograma" e "Alocar".

**Decision**: Usar `QLabel` overlay sobre a `QTableView`, controlado pelo sinal `stories_changed` do ViewModel.

**Rationale**:
- PySide6 nao tem componente nativo de "empty state" para QTableView.
- Um QLabel posicionado como overlay (via QStackedWidget ou layout z-order) e o padrao mais simples.
- A visibilidade do overlay e controlada pelo rowCount do modelo: 0 = mostra overlay, >0 = esconde.
- Desabilitacao de botoes segue o mesmo sinal.

**Alternatives considered**:
- Pintar mensagem via delegate customizado: Complexo e nao semantico. Rejeitado.
- Sobrescrever `paintEvent` do QTableView: Funcional mas mistura responsabilidades View/Model. Rejeitado.
- QStackedWidget com pagina de empty state: Viavel mas adiciona widget extra desnecessario. QLabel overlay e mais simples.

**Implementation approach**:
1. Criar `QLabel` centralizado como child da area central (acima do QTableView no layout, inicialmente invisivel).
2. No slot `_on_stories_changed`, verificar `table_model.rowCount()`:
   - Se 0: mostrar label, desabilitar `_action_schedule` e `_action_allocate`.
   - Se > 0: esconder label, habilitar botoes.
3. Texto: "Nenhuma historia cadastrada. Clique em '+ Nova' ou importe um arquivo Excel para comecar."
4. Estilizacao: cor texto `neutral-500`, font-size 14px, centralizado.

---

## R-004: Configuracao de Larguras Fixas e Stretch

**Contexto**: FR-015 define larguras fixas para 12 colunas e stretch para Nome. A MainWindow atualmente usa `resizeColumnsToContents()` e `setStretchLastSection(True)`.

**Decision**: Usar `QHeaderView.ResizeMode.Fixed` para todas as colunas exceto Nome, que usa `QHeaderView.ResizeMode.Stretch`.

**Rationale**:
- `setStretchLastSection(True)` nao serve porque Nome nao e a ultima coluna.
- `setSectionResizeMode(col, mode)` permite controle individual por coluna.
- Larguras definidas via `resizeSection(col, width)` apos configurar o modo.

**Alternatives considered**:
- `resizeColumnsToContents()` + restricoes: Nao garante larguras fixas exatas. Rejeitado.
- Delegate customizado com sizeHint: Over-engineering. `setSectionResizeMode` e suficiente.

**Implementation approach**:
1. Definir constante `COLUMN_WIDTHS` no `StoryTableModel` ou `MainWindow`:
   ```python
   COLUMN_WIDTHS = [60, 120, 50, 100, 80, -1, 100, 100, 120, 40, 90, 90, 60]
   # -1 = stretch (Nome)
   ```
2. No `_setup_central_widget`, apos criar a tabela, configurar header:
   ```python
   header = self._story_table.horizontalHeader()
   header.setStretchLastSection(False)
   for col, width in enumerate(COLUMN_WIDTHS):
       if width == -1:
           header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)
       else:
           header.setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)
           header.resizeSection(col, width)
   ```

---

## R-005: Tooltips para Colunas com Texto Truncado

**Contexto**: FR-014 exige tooltips para colunas Nome, Feature, Desenvolvedor e Dependencias quando texto e truncado.

**Decision**: Retornar o texto completo via `Qt.ItemDataRole.ToolTipRole` no `StoryTableModel.data()` para as colunas relevantes.

**Rationale**:
- QTableView renderiza tooltips automaticamente quando o modelo retorna dados para `ToolTipRole`.
- Nao e necessario delegate customizado — o comportamento padrao do Qt ja trata truncamento + tooltip.
- Retornar tooltip apenas para colunas que podem truncar (Feature, Nome, Desenvolvedor, Dependencias).

**Alternatives considered**:
- Tooltip em todas as colunas: Desnecessario para colunas curtas (SP, Onda). Rejeitado.
- Delegate com tooltip customizado: Over-engineering. O mecanismo nativo e suficiente.

**Implementation approach**:
- No `data()`, quando `role == Qt.ItemDataRole.ToolTipRole`, retornar o valor completo para colunas 1 (Feature), 5 (Nome), 7 (Desenvolvedor), 8 (Dependencias).

---

## R-006: Estilizacao QSS — Zebra, Selecao, Header

**Contexto**: FR-021/022/023 exigem zebra striping, selecao azul claro sem inversao, e header estilizado.

**Decision**: Ajustar o `stylesheet.qss` existente (EP-017) se necessario, e garantir que `setAlternatingRowColors(True)` esta ativo.

**Rationale**:
- O `StoryTableView` ja tem `setAlternatingRowColors(True)` (linha 74).
- O `stylesheet.qss` ja tem estilos extensivos para QTableView e QHeaderView.
- Verificar se a cor de selecao (#E6F0FA) e texto escuro ja estao definidos no QSS.

**Alternatives considered**:
- Estilizacao via delegate: Desnecessario quando QSS cobre o caso. Rejeitado.
- Configuracao programatica de palette: Menos mantenivel que QSS. Rejeitado.

**Implementation approach**:
1. Verificar estilos existentes no `stylesheet.qss` para QTableView::item:selected.
2. Ajustar se necessario para fundo #E6F0FA e texto escuro.
3. Verificar header com peso 600 e borda inferior.
