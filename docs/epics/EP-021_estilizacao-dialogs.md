# EP-021 — Estilizacao de Dialogs (GUI-005)

**Camada:** Interface & Experiencia

---

## Problema que Resolve

Todos os dialogs existentes (StoryDialog, DeveloperDialog, FeatureDialog, ConfirmDeleteDialog) implementados em EP-008 usam QFormLayout nativo sem estilizacao: bordas quadradas, espacamento apertado, sem icones nos botoes, sem validacao visual em tempo real, sem estados vazios orientativos. O StoryDialog nao permite atribuicao manual de desenvolvedor conforme RF-STORY-007. O feedback de import/export Excel e generico sem estilizacao. O resultado e uma experiencia inconsistente entre a tela principal (refatorada em EP-017/EP-018/EP-019/EP-020) e os dialogs, prejudicando a percepcao de qualidade (RNF-USAB-003, RNF-USAB-004).

## Objetivo (Valor Mensuravel)

Estilizar todos os dialogs com visual consistente via objectNames + QSS centralizado (do EP-017). Adicionar validacao em tempo real (on-blur) com indicadores de campo obrigatorio e estados de erro inline. Adicionar estados vazios orientativos em listas de dialogs. Adicionar dropdown de desenvolvedor no StoryDialog (modo edicao) conforme RF-STORY-007. Estilizar feedback de import/export Excel.

**Entregas concretas:**
- StoryDialog estilizado com campo Desenvolvedor (QComboBox) no modo edicao
- DeveloperDialog com icones nos botoes, hover effect, estado vazio
- FeatureDialog com formato "Onda N — Nome", estado vazio
- ConfirmDeleteDialog com icone warning-triangle.svg, botao vermelho, texto descritivo
- Progress/Result Dialogs para import/export estilizados
- Validacao on-blur em campos obrigatorios com feedback visual
- Estados vazios orientativos em todos os dialogs com listas

**Metricas de sucesso:**
- 100% dos dialogs com estilizacao via QSS centralizado
- Validacao on-blur funcional em campos obrigatorios
- Estados vazios exibidos quando listas estao vazias
- RF-STORY-007 (Atribuir Desenvolvedor Manualmente) habilitado na UI
- Testes existentes continuam passando sem regressao

## Alinhamento Estrategico

Conexao com as capacidades do produto definidas na secao 2.2 do SRS:
- **Capacidade 1 (Gestao de Backlog)**: StoryDialog com atribuicao manual de desenvolvedor (RF-STORY-007)
- **Capacidade 3 (Gestao de Desenvolvedores)**: DeveloperDialog estilizado com UX melhorada
- **Capacidade 2 (Gestao de Features)**: FeatureDialog estilizado com formato "Onda N — Nome"
- **Capacidade 7 (Integracao Excel)**: Dialogs de progresso/resultado para import/export
- **Transversal**: Consistencia visual em todos os dialogs, validacao em tempo real

## Personas Impactadas

| Persona (SRS §2.3) | Impacto |
|--------------------|---------|
| Scrum Master / Tech Lead | Atribuicao manual de desenvolvedor via StoryDialog, validacao em tempo real evita erros |
| Gerente de Projeto | Feedback visual claro em operacoes de import/export, dialogs mais profissionais |
| Product Owner | Interface consistente para apresentacao a stakeholders, menos erros de entrada |

## Jornadas / Casos de Uso Afetados

- UC-001: Criar e Priorizar Backlog — habilita (atribuicao manual de dev via RF-STORY-007)
- UC-001: Criar e Priorizar Backlog — contribui para (validacao em tempo real no StoryDialog)
- UC-004: Importar Backlog do Excel — contribui para (dialogs de progresso/resultado estilizados)
- CT-001 a CT-005: executaveis com dialogs estilizados

---

## Escopo

### Dentro do Escopo

**Requisitos Funcionais:**
- RF-STORY-007: Atribuir Desenvolvedor Manualmente — exposicao na UI via dropdown no StoryDialog (modo edicao)

**Requisitos Nao-Funcionais:**
- RNF-USAB-003: Acessibilidade basica (indicadores de campo obrigatorio, estados de erro visiveis)
- RNF-USAB-004: Curva de aprendizado <= 15 minutos (validacao em tempo real, estados vazios orientativos)
- RNF-CONF-002: Recuperacao de erros (mensagens de erro claras inline, dialogs nao crasham)
- RNF-MANT-001: Manutenibilidade (objectNames para QSS, codigo organizado)

**Artefatos Estruturais:**
- Arquitetura em camadas (SRS §6.1): Camada Presentation
- Padroes UI/UX (Constitution §XIX): MVVM com separacao View/ViewModel

**Componentes a implementar:**

| ID      | Componente             | Tipo          | Descricao |
|---------|------------------------|---------------|-----------|
| DLG-001 | StoryDialog            | REFATORACAO   | Estilizar via QSS, adicionar campo Desenvolvedor (QComboBox), validacao on-blur, indicador obrigatorio (*), area de erro inline |
| DLG-002 | DeveloperDialog        | REFATORACAO   | Icones nos botoes, item height 40px, hover effect via QSS, estado vazio |
| DLG-003 | FeatureDialog          | REFATORACAO   | Formato "Onda N — Nome", estilizacao consistente, estado vazio |
| DLG-007 | ConfirmDeleteDialog    | REFATORACAO   | Icone warning-triangle.svg 32x32px cor @warning, botao [Confirmar] @error bg + branco texto, texto descritivo |
| DLG-008 | Progress/Result Dialogs| REFATORACAO   | Progress dialog estilizado com QProgressBar, dialog de resultado com contagens |
| UX-002  | Atribuicao Manual Dev  | NOVO          | Campo "Desenvolvedor" no StoryDialog (modo edicao) com QComboBox: lista de devs + opcao "Nenhum" |
| UX-012  | Validacao em Tempo Real| NOVO          | Validacao on-blur: campo obrigatorio (*), erro visual inline (borda @error, mensagem em @error-light bg), contagem de caracteres |
| UX-013  | Estados Vazios         | NOVO          | Mensagens orientativas em DeveloperDialog, FeatureDialog quando listas vazias |

### Fora do Escopo

- ConfigDialog, DependencyDialog, MetricsDialog (ja estilizados na migracao em EP-018)
- Dialog "Sobre" → sera tratado em EP-022 (GUI-006)
- Import/Export Excel (logica de negocio) → EP-009

---

## Requisitos Funcionais Principais

| ID | Nome | Prioridade |
|----|------|------------|
| RF-STORY-007 | Atribuir Desenvolvedor Manualmente | Should Have |

**Funcionalidades de UI refatoradas:**

| Componente | Descricao | RFs Relacionados |
|------------|-----------|------------------|
| StoryDialog | Estilizacao + campo Desenvolvedor | RF-STORY-001/002, RF-STORY-007 |
| DeveloperDialog | Icones, hover, estado vazio | RF-DEV-001/002/003/004 |
| FeatureDialog | Formato "Onda N — Nome", estado vazio | RF-FEAT-001/002/003 |
| ConfirmDeleteDialog | Icone alerta, botao vermelho | RF-STORY-003, RF-DEV-003, RF-FEAT-003 |
| Progress/Result Dialogs | Estilizacao de import/export | UC-004 |

## Requisitos Nao-Funcionais Criticos

| ID | Nome | Metrica-alvo |
|----|------|-------------|
| RNF-USAB-003 | Acessibilidade Basica | Indicadores de campo obrigatorio (*), estados de erro visiveis |
| RNF-USAB-004 | Curva de Aprendizado | <= 15 minutos (validacao intuitiva, estados vazios orientativos) |
| RNF-CONF-002 | Recuperacao de Erros | Mensagens de erro inline claras, dialogs nao crasham |
| RNF-PERF-002 | Responsividade UI | <= 100ms abertura de dialogs |
| RNF-MANT-001 | Manutenibilidade | ObjectNames atribuidos para seletores QSS |

---

## Criterios de Aceite (Alto Nivel)

### StoryDialog
- [ ] **Dado** StoryDialog aberto, **Quando** inspeciono estilo, **Entao** vejo bordas arredondadas, espacamento 16px, padding 24px, titulo 16px weight 600
- [ ] **Dado** StoryDialog em modo edicao, **Quando** verifico campos, **Entao** vejo dropdown Desenvolvedor com lista de devs + "Nenhum"
- [ ] **Dado** StoryDialog, **Quando** seleciono desenvolvedor e salvo, **Entao** historia e atualizada com developer_id selecionado

### Validacao em Tempo Real
- [ ] **Dado** campo obrigatorio, **Quando** verifico label, **Entao** vejo asterisco (*) vermelho
- [ ] **Dado** campo obrigatorio vazio, **Quando** mudo foco (blur), **Entao** borda muda para @error e mensagem de erro inline aparece
- [ ] **Dado** formulario invalido, **Quando** verifico botao [Salvar], **Entao** esta desabilitado
- [ ] **Dado** campo de texto, **Quando** digito, **Entao** vejo contagem de caracteres restantes (ex: "45/200")

### DeveloperDialog
- [ ] **Dado** DeveloperDialog aberto, **Quando** verifico botoes, **Entao** vejo icones SVG ([+ Adicionar] [Editar] [Remover] [Fechar])
- [ ] **Dado** lista de desenvolvedores, **Quando** passo mouse sobre item, **Entao** vejo hover effect (@neutral-100)
- [ ] **Dado** nenhum desenvolvedor cadastrado, **Quando** abro DeveloperDialog, **Entao** vejo estado vazio: "Nenhum desenvolvedor cadastrado. Clique em 'Adicionar' para comecar."

### FeatureDialog
- [ ] **Dado** FeatureDialog aberto, **Quando** verifico lista, **Entao** vejo formato "Onda N — Nome da Feature"
- [ ] **Dado** nenhuma feature cadastrada, **Quando** abro FeatureDialog, **Entao** vejo estado vazio: "Nenhuma feature cadastrada."

### ConfirmDeleteDialog
- [ ] **Dado** ConfirmDeleteDialog aberto, **Quando** verifico layout, **Entao** vejo icone warning-triangle.svg (32x32px, cor @warning) a esquerda
- [ ] **Dado** ConfirmDeleteDialog, **Quando** verifico texto, **Entao** vejo "Excluir [ID] — [Nome]? Esta acao nao pode ser desfeita."
- [ ] **Dado** ConfirmDeleteDialog, **Quando** verifico botoes, **Entao** [Confirmar Exclusao] tem bg @error + texto branco

### Progress/Result Dialogs
- [ ] **Dado** import em andamento, **Quando** verifico dialog, **Entao** vejo "Importando dados..." com QProgressBar estilizada
- [ ] **Dado** import concluido, **Quando** verifico resultado, **Entao** vejo "Importacao concluida: X historias, Y features, Z avisos"
- [ ] **Dado** export concluido, **Quando** verifico resultado, **Entao** vejo "Exportacao concluida: X historias exportadas para [caminho]"

### Compatibilidade
- [ ] **Dado** testes existentes, **Quando** executo suite, **Entao** todos passam sem regressao
- [ ] **Dado** QSS do EP-017, **Quando** abro dialogs, **Entao** estilizacao e aplicada via objectNames

## KPIs / Metricas de Sucesso

| KPI | Metrica | Meta | Fonte SRS |
|-----|---------|------|-----------|
| Dialogs estilizados | % de dialogs com QSS | 100% (5 dialogs) | RNF-USAB-003 |
| Validacao on-blur | Campos com validacao | Componente, Nome (obrigatorios) | RNF-CONF-002 |
| Estados vazios | Dialogs com estado vazio | DeveloperDialog, FeatureDialog | RNF-USAB-004 |
| RF-STORY-007 | Dropdown Desenvolvedor funcional | 100% | RF-STORY-007 |
| Regressao | Testes falhando | 0 | RNF-MANT-001 |

## Plano de Validacao

| Tipo | Descricao | Referencia SRS |
|------|-----------|----------------|
| Teste Manual | Abrir StoryDialog em modo edicao: dropdown de Dev visivel e funcional | RF-STORY-007 |
| Teste Manual | Deixar campo obrigatorio vazio e mudar foco: borda vermelha + mensagem de erro aparece | RNF-CONF-002 |
| Teste Manual | Abrir DeveloperDialog sem devs cadastrados: mensagem de estado vazio visivel | RNF-USAB-004 |
| Teste Manual | Abrir FeatureDialog sem features: mensagem de estado vazio visivel | RNF-USAB-004 |
| Teste Manual | Abrir ConfirmDeleteDialog: icone de alerta, texto com ID/nome, botao vermelho | RNF-USAB-003 |
| Teste Manual | Importar Excel: progress dialog estilizado durante importacao, dialog de resultado com contagens | UC-004 |
| Teste Manual | Exportar Excel: progress dialog estilizado, dialog de resultado com caminho | UC-004 |
| Teste Unitario | Testar validacao de campos obrigatorios no StoryDialogViewModel | RNF-CONF-002 |
| Teste Unitario | Testar listagem de desenvolvedores para dropdown | RF-STORY-007 |
| Revisao de Codigo | Confirmar que objectNames estao atribuidos em todos os widgets que usam seletores QSS por #id | RNF-MANT-001 |
| Revisao de Codigo | Validar separacao View/ViewModel nos dialogs refatorados | Constitution §XIX |

---

## Dependencias

| Epico | Motivo |
|-------|--------|
| EP-008 | Interface grafica basica implementada — dialogs existentes a serem estilizados |
| EP-017 | QSS centralizado (DS-002) com seletores para dialogs, icones SVG (DS-005) para botoes e alerta, theme.py (DS-001) para cores |

## Riscos e Premissas

| Tipo | Descricao | Mitigacao |
|------|-----------|-----------|
| Risco | Validacao on-blur pode conflitar com logica de validacao existente no ViewModel | Manter validacao existente no ViewModel intacta; adicionar validacao visual como camada adicional na View |
| Risco | Atribuir objectNames pode impactar seletores QSS inesperadamente | Testar a aplicacao apos cada objectName adicionado; seletores QSS por #id sao mais especificos que por tipo |
| Risco | Campo Desenvolvedor no StoryDialog pode exigir alteracao na assinatura do ViewModel | Restricao: nao alterar assinatura publica existente. Adicionar novo signal/propriedade sem remover existentes |
| Risco | Progress dialogs podem bloquear UI se operacao for sincrona | Usar qasync para operacoes assincronas conforme Constitution §VIII |
| Premissa | PySide6 6.6.1+ suporta QProgressBar e estilizacao via QSS | Conforme SRS §2.4 |
| Premissa | Icones SVG do EP-017 ja estao disponiveis em assets/icons/ | Dependencia explicita de EP-017 |
| Premissa | Lista de desenvolvedores esta disponivel via DeveloperRepository | Implementado em EP-004 |

---

## Especificacoes Tecnicas (Referencia)

### Arquivos Impactados

| Arquivo | Acao | Descricao |
|---------|------|-----------|
| `src/backlog_manager/presentation/views/story_dialog.py` | EDITAR | Adicionar objectNames, campo Desenvolvedor (QComboBox), validacao on-blur, indicador obrigatorio (*), area de erro inline |
| `src/backlog_manager/presentation/views/developer_dialog.py` | EDITAR | Adicionar icones nos botoes, item height 40px, hover effect via QSS, estado vazio |
| `src/backlog_manager/presentation/views/feature_dialog.py` | EDITAR | Formato "Onda N — Nome", estilizacao consistente, estado vazio |
| `src/backlog_manager/presentation/views/confirm_delete_dialog.py` | EDITAR | Icone de alerta SVG, botao Confirmar vermelho, texto descritivo |
| `src/backlog_manager/presentation/viewmodels/story_dialog_viewmodel.py` | EDITAR | Adicionar propriedade para lista de desenvolvedores (para dropdown), validacao de campos |
| `src/backlog_manager/presentation/styles/stylesheet.qss` | EDITAR | Adicionar/ajustar seletores de objectName para botoes e widgets de dialogs (se necessario) |

### StoryDialog (DLG-001) — 480x440px (expandido para campo Dev)

**Layout:**
- Padding interno: 24px, espacamento entre campos: 16px
- Titulo: "Nova Historia" ou "Editar Historia: AUTH-001" — font-size 16px, weight 600
- Campos:
  - Componente: input texto, limite 50 chars, uppercase automatico (modo edicao: disabled)
  - Nome: input texto, limite 200 chars
  - Story Points: dropdown (3, 5, 8, 13)
  - Feature: dropdown com features carregadas + "Nenhuma"
  - **Desenvolvedor (NOVO — UX-002):** QComboBox com devs cadastrados + "Nenhum" (apenas modo edicao)
- Botoes: [Salvar] — QPushButton#btnSave bg @primary, cor branca, 36px; [Cancelar] — QPushButton#btnCancel bg @neutral-200, cor @neutral-700, 36px
- Inputs: border-radius @radius-md, border 1px solid @neutral-300, padding 8px 12px, focus: border @primary

### Validacao em Tempo Real (UX-012)

- Campos obrigatorios marcados com `*` vermelho no label
- Validacao on-blur (focusOut): se vazio, borda muda para @error, mensagem de erro inline abaixo com fundo @error-light
- Contagem de caracteres restantes em inputs de texto (ex: "45/200")
- Botao [Salvar] desabilitado se formulario invalido

### DeveloperDialog (DLG-002)

- Lista com items 40px altura
- Hover: fundo @neutral-100
- Botoes com icones SVG: [+ Adicionar] [Editar] [Remover] [Fechar]
- Estado vazio: "Nenhum desenvolvedor cadastrado. Clique em 'Adicionar' para comecar."
- Visual: texto @neutral-400, centralizado na area de lista, font-size @font-size-base

### FeatureDialog (DLG-003)

- Lista com formato "Onda N — Nome da Feature"
- Estado vazio: "Nenhuma feature cadastrada."
- Estilizacao consistente com DeveloperDialog

### ConfirmDeleteDialog (DLG-007) — 400x200px

- Layout: coluna esquerda com icone warning-triangle.svg (32x32px, cor @warning) + coluna direita com texto
- Texto: "Excluir [ID] — [Nome]? Esta acao nao pode ser desfeita."
- Botao [Confirmar Exclusao] — QPushButton#btnConfirmDelete bg @error, cor branca, 36px
- Botao [Cancelar] — bg @neutral-200, 36px

### Progress/Result Dialogs (DLG-008)

- Importar: "Importando dados..." com QProgressBar estilizada → resultado "Importacao concluida: X historias, Y features, Z avisos"
- Exportar: "Exportando dados..." → resultado "Exportacao concluida: X historias exportadas para [caminho]"
- Estilizacao consistente com demais dialogs (padding 24px, border-radius @radius-lg)

### Estados Vazios (UX-013)

- DeveloperDialog: "Nenhum desenvolvedor cadastrado. Clique em 'Adicionar' para comecar."
- FeatureDialog: "Nenhuma feature cadastrada."
- DependencyDialog (EP-018): "Nenhuma dependencia definida para esta historia." (se aplicavel)
- Visual: texto @neutral-400, centralizado na area de lista, font-size @font-size-base
