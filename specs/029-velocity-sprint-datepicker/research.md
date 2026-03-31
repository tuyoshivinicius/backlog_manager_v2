# Research: Velocidade em SP/Sprint e DatePicker Reutilizavel

**Feature Branch**: `029-velocity-sprint-datepicker`
**Date**: 2026-03-31

## R-001: Onde ocorre a conversao SP/Sprint → SP/dia?

**Decision**: A conversao ocorre exclusivamente na camada de Presentation (ConfigDialogViewModel), no momento de salvar/aplicar. O ViewModel expoe `sp_per_sprint` (int) e `workdays_per_sprint` (int) como propriedades, e calcula `velocity_per_day` como propriedade derivada (`sp_per_sprint / workdays_per_sprint`). Ao transferir para o dominio (via `_on_apply`), apenas `velocity_per_day` e passado.

**Rationale**: O dominio opera em "dias uteis" como unidade atomica. SP/Sprint e conveniencia de UX. Manter a conversao na Presentation respeita Clean Architecture (Principio I) e mantem o dominio desacoplado de conceitos de sprint.

**Alternatives considered**:
- Adicionar sp_per_sprint/workdays_per_sprint ao AllocationConfig (dominio): Rejeitado. Vazaria conceito de sprint para o dominio, violando Principio I.
- Converter na Application layer (DTO): Rejeitado. A conversao e puramente de apresentacao; o DTO `ExecuteAllocationInputDTO` ja recebe velocity em SP/dia e nao precisa mudar.

## R-002: Impacto na persistencia QSettings

**Decision**: Adicionar dois novos campos no grupo "allocation" do QSettings: `sp_per_sprint` (int, default 20) e `workdays_per_sprint` (int, default 10). O campo antigo `velocity` (float, SP/dia) e mantido para leitura na migracao mas nao e mais escrito.

**Rationale**: QSettings ja e usado para persistencia de configuracao de alocacao. Os novos campos sao a fonte de verdade. O campo antigo e lido apenas como fallback na migracao (se novos campos nao existem, usa defaults).

**Alternatives considered**:
- Converter velocity antigo (SP/dia) para SP/Sprint: Rejeitado. Sem saber os workdays_per_sprint originais, a conversao inversa e ambigua. Defaults seguros sao mais confiáveis.
- Remover campo velocity antigo imediatamente: Rejeitado. Manter para nao quebrar leituras de versao anterior caso de downgrade.

## R-003: Estrategia de migracao QSettings

**Decision**: Na `_load_from_qsettings()`, verificar se `sp_per_sprint` existe. Se nao existir (primeira execucao ou migracao de versao anterior), usar defaults (20, 10). O campo antigo `velocity` e ignorado (nao e lido nem convertido). Na proxima chamada a `_save_to_qsettings()`, os novos campos sao persistidos.

**Rationale**: Simplicidade e seguranca. Defaults de 20 SP/Sprint e 10 dias/sprint (= 2.0 SP/dia) sao equivalentes ao default antigo de velocity=2.0. O usuario ve valores razoaveis e pode ajustar.

**Alternatives considered**:
- Ler velocity antigo e tentar derivar sp_per_sprint (velocity * 10): Rejeitado. Assume workdays=10, o que pode nao ser correto. Defaults explicitos sao mais claros.

## R-004: Design do componente DatePicker

**Decision**: Criar `DatePicker(QDateEdit)` como subclasse de QDateEdit com:
- Calendar popup habilitado por default
- Display format `dd/MM/yyyy` por default
- Estilizacao via DESIGN_TOKENS (fonte, cores, borda)
- Suporte a `min_date` e `max_date` via construtor (opcionais)
- Signal `date_changed(date)` que emite `datetime.date` (nao QDate)

**Rationale**: QDateEdit ja fornece toda a funcionalidade necessaria. Subclassar (em vez de wrapper) minimiza codigo e mantem compatibilidade com QFormLayout. A estilizacao centralizada elimina duplicacao das 3 views que usam QDateEdit.

**Alternatives considered**:
- Wrapper QWidget com QDateEdit interno: Rejeitado. Adiciona complexidade desnecessaria (delegacao de metodos). Subclasse e mais simples.
- Componente custom com QCalendarWidget standalone: Rejeitado. Over-engineering. QDateEdit com calendarPopup ja oferece o comportamento desejado.

## R-005: Validacao de divisao por zero

**Decision**: Validacao dupla: (1) QSpinBox de workdays_per_sprint tem minimum=1 (impede 0 via UI), (2) ViewModel.validate() verifica workdays_per_sprint >= 1 como segunda barreira. A propriedade derivada `velocity_per_day` so e calculada apos validacao.

**Rationale**: Belt-and-suspenders. O spinbox previne input invalido, mas a validacao no ViewModel protege contra programacao direta (testes, futuras APIs).

**Alternatives considered**:
- Apenas validacao no ViewModel: Rejeitado. Melhor prevenir no UI tambem para feedback imediato.
- Validacao no dominio: Desnecessaria. O dominio ja valida `velocity > 0` no AllocationConfig.

## R-006: Label read-only de velocity_per_day derivada

**Decision**: Adicionar QLabel abaixo dos campos SP/Sprint e dias/sprint que exibe `"= X.X SP/dia"`. Atualizado dinamicamente via signal `valueChanged` dos QSpinBox. Estilizado como texto secundario (text-muted do DESIGN_TOKENS).

**Rationale**: Feedback visual imediato permite ao usuario validar mentalmente a conversao. Cor secundaria indica que e informacao derivada, nao editavel.

**Alternatives considered**:
- Tooltip no campo SP/Sprint: Rejeitado. Menos visivel, requer hover.
- Campo desabilitado (QDoubleSpinBox readonly): Rejeitado. QLabel e mais leve e semanticamente correto para informacao derivada.

## R-007: ConfigPanel vs ConfigDialog — diferenca de comportamento

**Decision**: ConfigPanel (painel lateral) segue a mesma mudanca que ConfigDialog: substitui QDoubleSpinBox de velocity por dois QSpinBox (SP/Sprint e dias uteis) + QLabel derivada. ConfigPanel nao persiste via QSettings (in-memory only, per ADR-007). As propriedades `velocity` (float, SP/dia) do ConfigPanel continuam existindo como propriedade derivada para compatibilidade com consumidores existentes.

**Rationale**: Manter consistencia visual entre ConfigDialog e ConfigPanel. A propriedade `velocity` derivada garante que codigo que le `config_panel.velocity` continua funcionando sem alteracao.

**Alternatives considered**:
- Manter ConfigPanel com SP/dia (so mudar ConfigDialog): Rejeitado. Inconsistencia visual confundiria o usuario.
