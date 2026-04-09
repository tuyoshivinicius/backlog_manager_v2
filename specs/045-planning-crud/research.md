# Research: Modulo de Planejamentos (CRUD Completo)

**Feature**: 045-planning-crud | **Date**: 2026-04-08

## R1: Estrategia de migracao de schema SQLite sem migration runner

**Decisao**: Migracao inline no `init_database()` com deteccao automatica de schema antigo via `PRAGMA table_info(Story)`.

**Racional**: O projeto nao possui migration runner (diretorio `migrations/` existe mas esta vazio). O schema atual usa `CREATE TABLE IF NOT EXISTS` executado via `executescript()` no startup. Adicionar um migration runner completo (e.g., Alembic) seria overengineering para uma unica migracao. A abordagem pragmatica eh:

1. Checar se a coluna `planning_id` ja existe em Story via `PRAGMA table_info(Story)`
2. Se nao existe, executar a migracao inline:
   - Criar tabela Planning
   - Inserir "Planejamento Inicial" como planning default
   - Adicionar coluna `planning_id` via `ALTER TABLE Story ADD COLUMN`
   - Atualizar todas as linhas orfas com o planning_id default
   - Recriar tabela Story com schema final (composite PK) via rename+copy+drop pattern
   - Recriar Story_Dependency com FK composta
3. Se ja existe, schema esta atualizado — noop

**Alternativas consideradas**:
- Alembic: Muito pesado para uma migracao; adicionaria dependencia desnecessaria
- Arquivo .sql de migracao versionado: Projeto nao tem runner para executa-lo
- Schema versioning table: Overengineering para escopo atual, mas pode ser adicionado futuramente se mais migracoes forem necessarias

## R2: Mudanca de PK do Story — composite key vs surrogate key

**Decisao**: Composite PRIMARY KEY `(planning_id, id)` na tabela Story.

**Racional**: O `id` do Story (ex: AUTH-001) eh digitado pelo usuario e representa um codigo externo (Jira/Azure DevOps). A spec exige que o mesmo ID possa existir em planejamentos diferentes (FR-014). As opcoes avaliadas:

- **Composite PK `(planning_id, id)`**: Natural e expressivo. A identidade de uma historia eh inerentemente composta pelo planejamento + codigo do ticket. Story_Dependency tambem usa composite FK, o que eh consistente pois dependencias sao sempre intra-planejamento (FR-012).
- **Surrogate `row_id` INTEGER PK**: Adicionaria um campo interno sem significado de dominio. Simplifica FKs mas obscurece a relacao planejamento-historia. Exigiria mudancas extensas na entidade Story e em todos os repositorios.

A composite PK eh a escolha natural para DDD (Constitution II) — a identidade da historia no dominio eh (planejamento, ticket_id).

**Alternativas consideradas**:
- Surrogate row_id: Rejeitado por adicionar complexidade desnecessaria e obscurecer identidade de dominio
- Prefixo de planning_id no story_id: Rejeitado por quebrar o modelo de ticket ID limpo

## R3: Impacto na entidade Story e repositorios existentes

**Decisao**: Adicionar `planning_id: int` como campo obrigatorio na entidade Story. Todos os metodos de StoryRepository que fazem queries recebem `planning_id` como parametro.

**Racional**: A Story precisa saber a qual planejamento pertence. A alternativa de scoping no repositorio (injetar planning_id no construtor do repo) foi rejeitada porque:
- O UoW cria repos uma vez por sessao, mas o planning ativo pode mudar durante a sessao
- Passar planning_id explicitamente nas queries eh mais seguro e explicito

Metodos afetados no StoryRepository Protocol:
- `get_all(planning_id: int)` → filtra por planejamento
- `get_by_id(planning_id: int, story_id: str)` → busca por composite key
- `exists(planning_id: int, story_id: str)` → verifica existencia no planejamento
- `get_by_status(planning_id: int, status: str)` → filtra por planejamento + status
- `get_by_developer(planning_id: int, developer_id: int)` → filtra por planejamento + dev
- `get_by_feature(planning_id: int, feature_id: int)` → filtra por planejamento + feature
- `get_max_id_number(planning_id: int, component: str)` → max dentro do planejamento
- `get_max_priority(planning_id: int)` → max dentro do planejamento
- `get_by_priority(planning_id: int, priority: int)` → dentro do planejamento
- `count_by_developer(planning_id: int, developer_id: int)` → conta no planejamento
- `add(story: Story)` → usa `story.planning_id` (ja esta no objeto)
- `update(story: Story)` → usa composite key do objeto
- `delete(planning_id: int, story_id: str)` → deleta por composite key

StoryDependencyRepository tambem precisa de `planning_id`:
- Todas as queries de dependencia recebem `planning_id` para scoping
- FKs referenciam `(planning_id, story_id)` na tabela Story

**Alternativas consideradas**:
- Scoping no construtor do repo: Rejeitado — UoW lifecycle nao se alinha com lifecycle do planning ativo
- Manter PK simples e adicionar UNIQUE constraint: Rejeitado — FK references ficariam ambiguas

## R4: Persistencia do ultimo planejamento ativo

**Decisao**: Usar QSettings (INI format) com chave `planning/last_active_id` (tipo `int`).

**Racional**: O projeto ja usa QSettings para persistir preferencias de UI (column widths, allocation config). A informacao do ultimo planejamento ativo eh uma preferencia de sessao do usuario, nao um dado de dominio — portanto QSettings eh o local correto (nao o banco de dados).

No startup:
1. Ler `planning/last_active_id` do QSettings
2. Verificar se o planejamento existe no banco
3. Se existe, carregar como ativo
4. Se nao existe (excluido, primeiro uso), apresentar dialogo de criacao

**Alternativas consideradas**:
- Coluna `is_active` na tabela Planning: Rejeitado — estado de sessao nao eh dado de dominio
- Arquivo .json de configuracao: Rejeitado — QSettings ja eh o padrao do projeto

## R5: Dialogo "Abrir Planejamento" — design de interacao

**Decisao**: QDialog com QTableWidget (nao QListWidget) exibindo nome, contagem de historias e data de ultima modificacao. Botoes de acao inline (editar/excluir) por linha usando `setCellWidget`.

**Racional**: A spec exige exibir 3 informacoes por planejamento (FR-016) + botoes de acao. Uma QTableWidget com 4 colunas (Nome, Historias, Ultima Modificacao, Acoes) eh a forma mais natural de apresentar esses dados tabulares. O botao "Abrir" fica no dialog button box padrao.

Para edicao de nome: ao clicar no botao editar, a celula de nome se torna editavel inline (QTableWidget `editItem`). Ao perder foco ou pressionar Enter, salva a alteracao.

Para exclusao: ao clicar no botao excluir, exibe QMessageBox de confirmacao com contagem de historias. O planejamento ativo nao exibe botao de exclusao (FR-006).

**Alternativas consideradas**:
- QListWidget com items customizados: Rejeitado — mais complexo para dados tabulares
- Dialog separado para edicao: Rejeitado — edicao inline eh mais fluida

## R6: Comportamento de bootstrap (primeiro uso)

**Decisao**: Na `run_application()`, apos `init_database()` e migracao, verificar se existem planejamentos. Se nenhum existe, forcar exibicao do dialogo de criacao antes de carregar a main window completa.

**Racional**: A spec exige que o sistema solicite a criacao de um planejamento ao iniciar com banco vazio (FR-013, Story 7). O fluxo:

1. `init_database()` — cria schema + migra dados orfaos (se houver)
2. Verificar contagem de planejamentos
3. Se zero planejamentos: exibir CreatePlanningDialog modal ANTES de `load_stories()`
4. Se existem planejamentos: carregar ultimo ativo via QSettings
5. Se ultimo ativo nao existe: exibir CreatePlanningDialog
6. Senao: carregar normalmente

Essa logica fica na `run_application()` em `app.py` ou no `MainWindowViewModel.initialize()`.

**Alternativas consideradas**:
- Criar planejamento default silenciosamente: Rejeitado — spec exige interacao do usuario
- Bloquear UI ate ter planejamento: Eh o que sera feito via dialog modal

## R7: Impacto na funcionalidade de Reset Planning

**Decisao**: A funcionalidade existente de "Reiniciar Planejamento" (reset) continua operando sobre as historias do planejamento ativo. Mudanca minima: `ResetPlanningUseCase` e `CountAffectedStoriesUseCase` recebem `planning_id` no DTO de entrada para scoping.

**Racional**: O reset ja opera sobre "todas as historias" — agora passa a operar sobre "todas as historias do planejamento ativo", que eh semanticamente o mesmo para o usuario. A unica mudanca eh adicionar `planning_id` ao filtro SQL.

Alem disso, o menu muda de "Novo Planejamento" para "Reiniciar Planejamento" (FR-011). O shortcut `Ctrl+Shift+N` pode ser reatribuido a "Novo Planejamento" (criacao) e o reset recebe um novo shortcut ou fica sem shortcut.

**Alternativas consideradas**: Nenhuma — eh a unica abordagem que faz sentido.

## R8: updated_at — estrategia de atualizacao

**Decisao**: O campo `updated_at` do Planning eh atualizado explicitamente nos use cases que modificam o planejamento ou suas historias.

**Racional**: SQLite nao suporta triggers `ON UPDATE` de forma tao elegante quanto outros bancos. As alternativas:

- **Trigger SQLite**: Possivel com `CREATE TRIGGER`, mas adiciona logica de negocio no banco (viola Constitution II - DDD).
- **Atualizacao explicita no use case**: Mais alinhado com Clean Architecture — o use case sabe quando uma operacao significativa aconteceu e atualiza o timestamp. Operacoes que atualizam `updated_at`:
  - Renomear planejamento
  - Criar/editar/excluir historia no planejamento
  - Importar historias
  - Alocar/agendar historias
  - Resetar planejamento

**Alternativas consideradas**:
- SQLite trigger: Rejeitado — logica de negocio no banco viola DDD
- Nao rastrear updated_at: Rejeitado — spec exige exibir data de ultima modificacao (FR-016)
