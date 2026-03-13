# Quickstart: Script de Seed para Teste de Alocação

## Pré-requisitos

- Python 3.11+
- Poetry instalado
- Dependências do projeto instaladas (`poetry install`)

## Uso Básico

### Gerar dados de teste no banco padrão

```bash
python scripts/seed_test_backlog.py
```

### Gerar dados em banco customizado

```bash
python scripts/seed_test_backlog.py --db-path ./test_data.db
```

### Limpar e regenerar dados

```bash
python scripts/seed_test_backlog.py --clean
```

### Combinar opções

```bash
python scripts/seed_test_backlog.py --clean --db-path ./test_data.db
```

## Verificação dos Dados

Após executar o script, verifique os dados gerados:

```bash
# Via sqlite3
sqlite3 $APPDATA/BacklogManager/data/backlog.db "SELECT COUNT(*) FROM Developer"  # 7
sqlite3 $APPDATA/BacklogManager/data/backlog.db "SELECT COUNT(*) FROM Feature"    # ~30
sqlite3 $APPDATA/BacklogManager/data/backlog.db "SELECT COUNT(*) FROM Story"      # 150-200
sqlite3 $APPDATA/BacklogManager/data/backlog.db "SELECT COUNT(*) FROM Story_Dependency"  # 80-120
```

## Testando com o Motor de Alocação

Após gerar os dados, execute o motor de alocação:

```bash
# Via aplicação GUI
poetry run backlog-manager

# Ou via testes de integração
poetry run pytest tests/integration/ -k allocation
```

## Executando Testes do Script

```bash
# Todos os testes do script
poetry run pytest tests/integration/test_seed_backlog.py -v

# Apenas teste de geração
poetry run pytest tests/integration/test_seed_backlog.py::test_seed_creates_expected_entities -v

# Apenas teste de ciclos
poetry run pytest tests/integration/test_seed_backlog.py::test_no_cycles_in_dependencies -v
```

## Troubleshooting

### Erro: "Banco de dados já contém dados"

O script falha se houver dados existentes (sem `--clean`):

```bash
# Solução: use --clean
python scripts/seed_test_backlog.py --clean
```

### Erro: "Diretório não existe"

Se `--db-path` aponta para diretório inexistente:

```bash
# Solução: crie o diretório primeiro
mkdir -p ./data
python scripts/seed_test_backlog.py --db-path ./data/test.db
```

### Performance lenta

O script deve completar em < 5 segundos. Se demorar mais:

1. Verifique se não há outros processos acessando o banco
2. Use banco local (não em rede)
3. Verifique espaço em disco
