# Log de Correcao: [Titulo Curto]

**Data**: YYYY-MM-DD
**Issue/Ticket**: [Referencia]
**Autor**: [Nome]

## 1. Problema

### Descricao
[Descricao clara do problema observado]

### Sintomas
- [Sintoma 1]
- [Sintoma 2]

### Reproducao
```bash
# Passos para reproduzir
poetry run python scripts/seed_test_backlog.py --clean
# ... comandos adicionais
```

### Seed Utilizada
- `random_seed`: [valor]

## 2. Diagnostico

### Logs Relevantes
```
[Colar linhas de log relevantes]
```

### Metricas Antes da Correcao
| Metrica | Valor |
|---------|-------|
| `total_time_seconds` | |
| `stories_allocated` | |
| `deadlocks_detected` | |
| `max_idle_violations_detected` | |

### Causa Raiz
[Explicacao da causa raiz do problema]

## 3. Mudanca

### Arquivos Modificados
- `src/backlog_manager/domain/services/allocation_service.py`
  - [Descricao da mudanca]

### Codigo Alterado
```python
# Antes
[codigo original]

# Depois
[codigo corrigido]
```

### Justificativa Tecnica
[Por que essa mudanca resolve o problema]

## 4. Resultado

### Metricas Apos Correcao
| Metrica | Antes | Depois | Delta |
|---------|-------|--------|-------|
| `total_time_seconds` | | | |
| `stories_allocated` | | | |
| `deadlocks_detected` | | | |

### Testes Executados
```bash
poetry run pytest tests/ -v
```

### Status da Suite de Testes
- [ ] Todos os testes passam
- [ ] Cobertura >= 80%
- [ ] Complexidade ciclomatica <= 15

### Performance
- [ ] <= 5s para 100 historias
- [ ] <= 30s para 500 historias

## 5. Validacao

### Checklist Final
- [ ] Problema resolvido
- [ ] Sem regressoes
- [ ] Logs claros e uteis
- [ ] Documentacao atualizada (se necessario)

### Observacoes
[Notas adicionais, se houver]
