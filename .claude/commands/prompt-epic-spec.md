---
description: Create an optimized prompt for feature specification from an epic description.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

The text the user typed after `/prompt-epic-spec` is the epic specification request. This typically includes the epic code (e.g., `EP-005`) and possibly a brief description.

Given that input, do this:

1. **Parse the epic code from $ARGUMENTS**:
   - Extract the epic code pattern `EP-NNN` (e.g., `EP-005`, `EP-001`)
   - If no valid epic code found: ERROR "Codigo do epico nao encontrado. Use o formato EP-NNN (ex: EP-005)"
   - Store the numeric part (NNN) for later use in output filename

2. **Locate the epic file**:
   - Search for the epic file in `docs/epics/` matching pattern `EP-{NNN}_*.md`
   - Example: `EP-005` → `docs/epics/EP-005_gestao-de-dependencias.md`
   - If file not found: ERROR "Arquivo do epico EP-{NNN} nao encontrado em docs/epics/"

3. **Read context files**:
   - **Epic file**: The located epic file (mandatory)
   - **Constitution**: `.specify/memory/constitution.md` (mandatory)
   - **SRS**: `srs.md` (mandatory - source of truth)
   - **Reference prompts**: `docs/prompts/specs/prompt_*.md` (for format reference)
   - **ROADMAP**: `docs/epics/ROADMAP.md` (for dependency mapping)

4. **Analyze the epic content**:
   - **Architectural layer**: Identify which layer (Fundacao, Dominio Core, Servicos de Negocio, Interface & Experiencia)
   - **Functional requirements**: Extract RF-xxx identifiers and descriptions
   - **Non-functional requirements**: Extract RNF-xxx identifiers and metrics
   - **Dependencies**: Identify predecessor epics (EP-001, EP-002, etc.)
   - **Conflicts and gaps**: Compare epic requirements vs. existing code vs. SRS to detect inconsistencies
   - **Acceptance criteria**: Extract Given/When/Then scenarios

5. **Determine the appropriate role/persona**:
   Based on the epic's architectural layer:
   - **Fundacao**: Engenheiro de Software Senior especializado em Clean Architecture, infraestrutura Python, banco de dados SQLite
   - **Dominio Core**: Arquiteto de Software com especializacao em DDD, entidades ricas, value objects, validacoes
   - **Servicos de Negocio**: Arquiteto de Software com especializacao em Domain Services, Application Layer, Use Cases
   - **Interface & Experiencia**: Especialista em UI/UX com PySide6, MVVM, experiencia do usuario

6. **Build the input section**:
   List all files that MUST be read before generating the specification:
   - The epic file itself
   - `srs.md` with relevant section references (§x.x)
   - `.specify/memory/constitution.md`
   - Reference specs from predecessor epics (if any)
   - Relevant existing code files based on dependencies
   - Repository protocols, entities, services that will be extended

7. **Build the context section**:
   - **Projeto**: Backlog Manager v2 description
   - **Stack Tecnica**: Python 3.11+, PySide6, SQLite, aiosqlite, Pydantic, pytest, Clean Architecture
   - **Estado Atual do Codigo**: What's implemented (from predecessor epics) vs. what's pending (this epic)
   - **Conflitos e Lacunas Conhecidos**: Numbered list of detected conflicts/gaps that MUST be resolved in the spec

8. **Build the task section**:
   - Clear, objective description of what the spec must cover
   - List all RF-xxx requirements in scope
   - Explain what architectural artifacts will be created/extended
   - Emphasize what is NOT in scope (predecessor/successor epic responsibilities)

9. **Build the rules section**:
   Generate quality rules specific to this epic:
   - Bidirectional traceability (FR-xxx ↔ RF-xxx)
   - Existing code as baseline (don't redefine what exists)
   - Explicit conflict resolution (ADR for each conflict)
   - Clear separation of responsibilities (Domain vs. Application vs. Repository)
   - Exact error messages (without accents, per SRS §8.2)
   - Testability requirements
   - No overlap with other epics
   - Naming consistency
   - Async operations (if applicable)
   - Transactional integrity (if applicable)
   - Reference to predecessor patterns (if applicable)

10. **Generate the optimized prompt**:
    - Use the XML-like section format: `<role>`, `<context>`, `<input>`, `<task>`, `<rules>`
    - **DO NOT** define output format or delivery method (this is a strict requirement)
    - Use Portuguese for content, keeping technical terms in English
    - Include all detected conflicts in the context section

11. **Save the prompt file**:
    - Output path: `docs/prompts/specs/prompt_{NNN}.md`
    - Example: EP-005 → `docs/prompts/specs/prompt_005.md`
    - If file already exists, overwrite with the new optimized version

12. **Report completion**:
    - Confirm the prompt was created successfully
    - Show the output file path
    - List key improvements made to the original prompt request

## Quality Guidelines

### Prompt Engineering Best Practices

- **Specificity**: Be precise about what the spec should cover, avoiding vague instructions
- **Context richness**: Provide enough background for the AI to make informed decisions
- **Conflict visibility**: Surface all known conflicts explicitly so they get resolved
- **Traceability**: Ensure every requirement can be traced back to source documents
- **Actionability**: The generated prompt should be executable without further clarification

### Format Consistency

Follow the exact format of existing prompts in `docs/prompts/specs/`:
- Title: `# Prompt: [Epic Title in Portuguese]`
- Sections in order: `<role>`, `<context>`, `<input>`, `<task>`, `<rules>`
- Context subsections: `## Projeto`, `### Stack Tecnica`, `### Estado Atual do Codigo`, `### Conflitos e Lacunas Conhecidos`
- Input: Numbered list of mandatory files to read
- Rules: Numbered list of quality requirements

### What NOT to Include

- **Output format**: The prompt MUST NOT specify how the spec should be formatted or delivered
- **Implementation details**: The prompt should focus on WHAT, not HOW
- **Time estimates**: No scheduling or timeline references
- **Specific file structures**: Let the spec author decide based on context
