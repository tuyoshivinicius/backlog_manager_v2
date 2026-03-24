# Research: EP-015 Melhoria Iterativa dos Algoritmos de Alocacao

**Date**: 2026-03-12

## Research Tasks

### 1. Logging em Metodos Estaticos de Domain Services

**Decision**: Usar logger no nivel de modulo com `logging.getLogger(__name__)`

**Rationale**:
- `AllocationService` usa `@staticmethod` em todos os metodos, entao nao ha `self.logger` disponivel
- Loggers no nivel de modulo sao cacheados pelo sistema de logging do Python
- Cada modulo obtem um logger nomeado pelo caminho do modulo (`backlog_manager.domain.services.allocation_service`)
- Metodos estaticos podem acessar facilmente o logger do modulo
- Nomes de logger hierarquicos permitem controle fino de niveis de log

**Alternatives considered**:
- Logger como parametro de metodo: Rejeitado pois aumentaria assinatura de todos os metodos
- Logger de classe: Nao compativel com `@staticmethod`
- Injecao de dependencia: Over-engineering para este caso

### 2. Logging de Dataclasses de Metricas (AllocationMetrics)

**Decision**: Log agregado no final do metodo com sumario de metricas

**Rationale**:
- AllocationMetrics acumula 16 contadores durante execucao
- Logar cada atualizacao de contador seria excessivo e impactaria performance
- Log de sumario no final captura estado completo
- Usar `extra` dict para dados estruturados facilita parsing posterior

**Alternatives considered**:
- Log por metrica individual: Rejeitado por overhead
- Callback de metrica: Over-engineering, adiciona complexidade

**Implementation pattern**:
```python
logger.info(
    "Alocacao completa: %d/%d historias (%.2fs, %d ondas, %d iteracoes)",
    metrics.stories_allocated,
    metrics.stories_processed,
    metrics.total_time_seconds,
    metrics.waves_processed,
    metrics.total_iterations,
    extra={
        "allocation_metrics": {
            "stories_allocated": metrics.stories_allocated,
            # ... demais campos
        }
    }
)
```

### 3. Performance de Logging em Loops Apertados

**Decision**: Usar guards `logger.isEnabledFor()` antes de logs DEBUG em loops

**Rationale**:
- Formatacao de strings e cara (f-strings, formatacao %)
- Se DEBUG esta desabilitado, pular formatacao completamente
- Overhead minimo mesmo em loops apertados
- Exemplo de impacto: 200 historias x 5 iteracoes = 1000 entradas de log evitadas se DEBUG desabilitado

**Implementation pattern**:
```python
if logger.isEnabledFor(logging.DEBUG):
    logger.debug(
        "Processando historia %s (SP=%s, eligible_count=%d)",
        story.id,
        story.story_points.value if story.story_points else None,
        len(eligible)
    )
```

**Alternatives considered**:
- Lazy formatting com `%s`: Menos legivel, Python 3 prefere % com args
- Loggers custom com caching: Over-engineering

### 4. Pontos de Decisao no Algoritmo

**Decision**: Logar o "porque" alem do "que" em pontos de decisao criticos

**Rationale**:
- FR-002 requer justificativa para cada decisao de selecao de desenvolvedor
- Pontos de decisao mostram logica do algoritmo
- Facilita diagnostico de problemas de distribuicao

**Key decision points identified**:
| Ponto de Decisao | Nivel | Informacao a Logar |
|------------------|-------|-------------------|
| Selecao de desenvolvedor | DEBUG | Motivo (dependency_owner vs load_balancing) |
| Deteccao de deadlock | WARNING | Historias bloqueadas, onda |
| Violacao de ociosidade | WARNING/INFO | Dev, dias ociosos, onda |
| Ajuste de data | DEBUG | Historia, nova data, motivo |
| Inicio/fim de onda | INFO | Numero da onda, qtd historias |
| Conclusao de alocacao | INFO | Todas 16 metricas de AllocationMetrics |

### 5. Niveis de Log Recomendados para o Algoritmo

**Decision**: Mapeamento de niveis conforme especificacao e constituicao

| Cenario | Nivel | Justificativa |
|---------|-------|---------------|
| Entrada do algoritmo (`allocate_stories`) | INFO | FR-005: Marca inicio de operacao principal |
| Inicio/fim de onda | INFO | FR-005: Transicoes importantes de fase |
| Sucesso de alocacao | DEBUG | FR-002: Operacao normal, alto volume |
| Conflito detectado + resolucao | DEBUG | Detalhes taticos |
| Deadlock detectado | WARNING | FR-003: Anormal mas recuperavel |
| Violacao de dependencia corrigida | DEBUG | Detalhes de validacao |
| Conflito de periodo resolvido | DEBUG | Detalhes de estabilizacao |
| Violacao de ociosidade | WARNING/INFO | FR-004: Flag de problema potencial |
| Estabilizacao completa | INFO | Fim de fase de estabilizacao |
| Sumario de metricas | INFO | FR-001: Dados agregados de performance |

### 6. Integracao com Logger Existente

**Decision**: Usar `get_logger()` existente de `infrastructure/logging/logger_config.py`

**Rationale**:
- Configuracao ja implementa requisitos da Constituicao (Principio XVII)
- Rotacao de 10MB com 3 backups
- Formato ISO 8601 para timestamp
- Hierarquia `backlog_manager.*` ja estabelecida

**Implementation**:
```python
# Em allocation_service.py (nivel de modulo)
from backlog_manager.infrastructure.logging import get_logger

logger = get_logger("domain.services.allocation_service")
```

**Note**: Usar `get_logger()` ao inves de `logging.getLogger()` diretamente para garantir que setup_logging() foi chamado.

## Riscos e Mitigacoes

| Risco | Probabilidade | Impacto | Mitigacao |
|-------|--------------|---------|-----------|
| Overhead de performance | Baixa | Media | Guards `isEnabledFor()` em loops |
| Logs excessivos em DEBUG | Media | Baixa | Log periodico (cada N iteracoes) |
| Formatacao de strings | Media | Baixa | Usar args posicionais `%s`, nao f-strings |
| Log de dados sensiveis | Baixa | Baixa | Logs locais apenas (clarificado em spec) |

## Dependencias

- **Nenhuma nova dependencia** - Usar `logging` stdlib e `get_logger()` existente
- EP-014 (seed script) ja implementado para dados de teste reproduziveis
