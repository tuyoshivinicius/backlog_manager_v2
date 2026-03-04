---
description: Refine or create epics from natural language descriptions with interactive gap clarification. (project)
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

The text the user typed after `/prompt-epic-refinement` is a natural language description of an epic. This may include an optional epic code (e.g., `EP-010`) for refining an existing epic, or just a description for creating a new one.

Given that input, execute the following 10-step process:

### Etapa 1 - Analise da Entrada

1. **Receive and validate input**:
   - If `$ARGUMENTS` is empty: ERROR "Descricao do epico nao fornecida. Por favor, descreva o epico que deseja criar ou refinar."
   - Store the description for analysis

### Etapa 2 - Deteccao de Epico Existente

1. **Extract epic code from description** (if present):
   - Search for pattern `EP-\d{3}` (e.g., EP-001, EP-010)
   - Examples: "EP-010 precisa incluir testes e2e" → EP-010 extracted

2. **Determine operation mode**:
   - **If epic code found**:
     - Search for file matching `docs/epics/EP-{NNN}_*.md`
     - If file exists: Set mode = **REFINAR**
     - If file not found: ERROR "Epico EP-{NNN} nao encontrado em docs/epics/"
   - **If no epic code found**:
     - Set mode = **CRIAR NOVO**

### Etapa 3 - Carregar Contexto

Read the following files to build context:

1. **Constitution** (mandatory): `.specify/memory/constitution.md`
   - Extract the 21 principles for validation
   - Pay special attention to: Clean Architecture (I), DDD (II), Repository Pattern (III), Async Programming (VIII), Testing Strategy (XIV), Error Handling (XVI)

2. **SRS** (mandatory): `srs.md`
   - Source of truth for all requirements (RF-*, RNF-*)
   - Reference for use cases (UC-001 to UC-005)
   - Reference for test scenarios (CT-001 to CT-005)

3. **Existing epics** (for cross-validation): `docs/epics/EP-*.md`
   - Extract all RF assignments to prevent overlap
   - Extract all dependencies to validate consistency
   - Identify next available epic code (for CRIAR mode)

4. **Do NOT read**: `docs/epics/ROADMAP.md`

### Etapa 4 - Analise de Gaps e Lacunas

Analyze the user's description against the epic template to identify missing information:

| Gap Category | Question to Resolve |
|--------------|---------------------|
| **Camada arquitetural** | Qual camada? (Fundacao / Dominio Core / Servicos de Negocio / Interface & Experiencia / Integracao & Otimizacao) |
| **Requisitos Funcionais** | Quais RF-xxx estao no escopo? |
| **Requisitos Nao-Funcionais** | Quais RNF-xxx sao criticos? |
| **Dependencias** | Quais epicos sao pre-requisito? (EP-xxx) |
| **Escopo** | O que esta dentro/fora do escopo? |
| **Criterios de Aceite** | Como validar a entrega? (Dado/Quando/Entao) |
| **Personas** | Quais perfis sao impactados? (Scrum Master, Gerente de Projeto, Product Owner) |
| **Problema** | Qual problema especifico este epico resolve? (referencia ao SRS) |
| **Objetivo** | Qual valor mensuravel sera entregue? |

For **REFINAR mode**: Compare existing epic content with user description to identify what needs updating.

### Etapa 5 - Clarificacao Interativa

For each gap identified in Etapa 4, ask clarification questions:

**Rules**:
- Maximum 5 questions per interaction (prioritize most critical)
- Offer options when possible (based on SRS content)
- Accept "pular" as response to use defaults
- Incorporate answers into the epic

**Format**:
```markdown
## Clarificacao Necessaria

Para completar o [refinamento/criacao] do epico, preciso esclarecer:

1. **[Categoria]**: [Pergunta especifica]
   - Opcao A: [descricao]
   - Opcao B: [descricao]
   - Opcao C: [outro]

2. **[Categoria]**: [Pergunta especifica]
   ...

Por favor, responda cada item ou indique "pular" para usar padroes.
```

**After receiving answers**: Continue to Etapa 6 with the gathered information.

### Etapa 6 - Validacao de Consistencia

#### 6.1 - Consistencia com Constitution.md

Verify alignment with relevant constitution principles:

| Principio | Verificacao |
|-----------|-------------|
| **I. Clean Architecture** | Epico respeita separacao em 4 camadas? |
| **II. DDD** | Entidades ricas, value objects, domain services definidos? |
| **III. Repository Pattern** | Interfaces em Domain, implementacoes em Infrastructure? |
| **VIII. Async Programming** | Operacoes I/O sao assincronas? |
| **XIV. Testing Strategy** | Plano de validacao inclui cobertura adequada (80%+)? |
| **XVI. Error Handling** | Excecoes seguem hierarquia definida (BacklogManagerException)? |

If violations found: Report to user and request correction before proceeding.

#### 6.2 - Consistencia Entre Epicos

Verify conflicts with existing epics:

| Conflito | Verificacao |
|----------|-------------|
| **Sobreposicao de RFs** | Nenhum RF deve ser escopo principal de 2 epicos |
| **RNFs transversais** | RNF-MANT-* devem referenciar "Conforme estabelecido em EP-001" |
| **Dependencias ciclicas** | Epico nao pode depender de epico com numero maior |
| **Sequencia de camadas** | Fundacao < Dominio < Servicos < Interface < Integracao |

If conflicts found: Report to user and request resolution before proceeding.

### Etapa 7 - Determinar Codigo do Epico

1. **For REFINAR mode**:
   - Use the existing epic code (EP-XXX)
   - Preserve the existing filename

2. **For CRIAR mode**:
   - List all existing epic codes in `docs/epics/`
   - Calculate next code: `EP-{max_existing + 1}`
   - Generate kebab-case name from epic title
   - Example: "Testes de Integracao E2E" → `EP-010_testes-de-integracao-e2e.md`

### Etapa 8 - Gerar/Atualizar Conteudo do Epico

Generate the epic file with all 14 mandatory sections:

```markdown
# EP-NNN — [Nome do Epico]

**Camada:** [Fundacao | Dominio Core | Servicos de Negocio | Interface & Experiencia | Integracao & Otimizacao]

---

## Problema que Resolve
[Descricao especifica ancorada no SRS — qual dor ou lacuna este epico endereca]

## Objetivo (Valor Mensuravel)
[O que se alcanca com a entrega deste epico, derivado das capacidades da secao 2.2]

## Alinhamento Estrategico
[Conexao com as 7 capacidades do produto definidas na secao 2.2 do SRS]

## Personas Impactadas
| Persona (SRS §2.3) | Impacto |
|---------------------|---------|
| Scrum Master / Tech Lead | [como e afetado] |
| Gerente de Projeto | [como e afetado] |
| Product Owner | [como e afetado] |

## Jornadas / Casos de Uso Afetados
- UC-xxx: [nome] — [habilita / contribui para (completo em EP-yyy)]
- CT-xxx: [executavel apos este epico? Sim/Parcial]

---

## Escopo

### Dentro do Escopo
**Requisitos Funcionais:**
- RF-xxx-yyy: [descricao curta]

**Requisitos Nao-Funcionais:**
- RNF-xxx-yyy: [descricao curta]

**Artefatos Estruturais do SRS:**
- [Se aplicavel: Schema ER (§6.4), Maquina de Estados (§6.5), Hierarquia de Excecoes (§7.3), Regras Implicitas (§8.3), Fluxo de Alocacao (§6.2)]

### Fora do Escopo
- [item] → sera tratado em EP-xxx

---

## Requisitos Funcionais Principais
| ID | Nome | Prioridade |
|----|------|------------|
| RF-xxx-yyy | ... | Must / Should / Could Have |

## Requisitos Nao-Funcionais Criticos
| ID | Nome | Metrica-alvo |
|----|------|-------------|
| RNF-xxx-yyy | ... | [valor do SRS ou "Conforme EP-001"] |

---

## Criterios de Aceite (Alto Nivel)
- [ ] **Dado** [contexto], **Quando** [acao], **Entao** [resultado esperado]
- [ ] [Criterio verificavel com referencia ao SRS]

## KPIs / Metricas de Sucesso
| KPI | Metrica | Meta | Fonte SRS |
|-----|---------|------|-----------|
| ... | ... | ... | RNF-xxx ou qualitativo |

## Plano de Validacao
| Tipo | Descricao | Referencia SRS |
|------|-----------|----------------|
| Testes Unitarios | [o que cobrir] | RF-xxx |
| Testes Integracao | [o que cobrir] | - |
| Cenario de Teste | [qual CT executar] | CT-xxx |
| Teste Manual | [fluxo a validar] | UC-xxx |
| Revisao de Codigo | [padrao a verificar] | RNF-MANT-xxx |

---

## Dependencias
| Epico | Motivo |
|-------|--------|
| EP-xxx | [razao especifica — qual artefato ou RF e pre-requisito] |

*Sem dependencias* — se for o caso.

## Riscos e Premissas
| Tipo | Descricao | Mitigacao |
|------|-----------|-----------|
| Risco | [especifico ao projeto] | [acao concreta] |
| Premissa | [suposicao assumida, referenciar SRS §2.5 quando aplicavel] | — |
```

### Etapa 9 - Salvar Arquivo

1. **Determine file path**:
   - Format: `docs/epics/EP-{NNN}_{nome-kebab-case}.md`
   - Example: `docs/epics/EP-010_testes-de-integracao-e2e.md`

2. **Write file**:
   - For **REFINAR**: Overwrite existing file
   - For **CRIAR**: Create new file

### Etapa 10 - Confirmar Conclusao

Report completion to user:

```markdown
## Epico [Criado/Refinado] com Sucesso

**Arquivo:** `docs/epics/EP-{NNN}_{nome}.md`

**Modo:** [CRIAR NOVO / REFINAR]

**Melhorias aplicadas:**
- [lista de secoes atualizadas ou adicionadas]

**Validacoes realizadas:**
- [x] Consistencia com Constitution.md
- [x] Sem sobreposicao de RFs com outros epicos
- [x] Dependencias validas

**Proximos passos sugeridos:**
- Executar `/prompt-epic-spec EP-{NNN}` para gerar prompt de especificacao
- Revisar criterios de aceite com stakeholders
- Atualizar ROADMAP.md se necessario
```

---

## Regras de Qualidade

Follow these rules in order of precedence (lower number prevails):

1. **Rastreabilidade total**: Todo RF/RNF referenciado deve existir no SRS. Nenhum requisito inventado.

2. **Sem sobreposicao**: Nenhum RF pode ser escopo principal de 2+ epicos. Se ja atribuido a outro epico, referencie como dependencia.

3. **Coesao por bounded context**: Agrupar RFs do mesmo dominio/prefixo no mesmo epico (RF-STORY-*, RF-DEV-*, etc.).

4. **Ordenacao por camada**: Sequencia deve respeitar: Fundacao → Dominio Core → Servicos de Negocio → Interface & Experiencia → Integracao & Otimizacao.

5. **Independencia pos-dependencia**: Epico deve ser implementavel e testavel de forma independente apos suas dependencias serem satisfeitas.

6. **Alinhamento com Constitution**: Todo epico deve estar em conformidade com os 21 principios da constituicao do projeto.

7. **Objetividade**: Conteudo deve ser especifico e rastreavel ao SRS. Evitar frases genericas. Se uma afirmacao nao pode ser vinculada a um ID ou secao do SRS, ela provavelmente e generica demais.

8. **Mensagens de erro sem acentos**: Conforme SRS §8.2, todas as mensagens de erro devem ser sem acentos.

---

## What NOT to Include

- **Output format**: The epic should not specify how specs should be formatted
- **Implementation details**: Focus on WHAT, not HOW
- **Time estimates**: No scheduling or timeline references
- **Generic content**: Every statement must be traceable to SRS
