# Research: EP-008 Interface Grafica

## 1. Integracao asyncio <-> Qt Event Loop

**Decisao**: Usar qasync como biblioteca de integracao.

**Racional**:
- qasync e a biblioteca mais madura e mantida para integracao asyncio/Qt
- Suporta PySide6 oficialmente
- Fornece decoradores @asyncSlot() e @asyncClose para facilitar desenvolvimento
- Para Python 3.11+ usa: asyncio.run(main(app), loop_factory=QEventLoop)
- Permite run_in_executor() para tarefas CPU-intensivas

**Alternativas Consideradas**:
1. PySide6.QtAsyncio - rejeitado por nao implementar eventos de rede (DNS, Sockets)
2. qtinter - rejeitado por ser menos maduro que qasync
3. Thread separada - rejeitado por adicionar complexidade de sincronizacao

## 2. Testes de GUI com pytest-qt

**Decisao**: Usar pytest-qt com fixtures customizadas para integracao com qasync.

**Racional**:
- pytest-qt e o plugin padrao para testes de Qt em Python
- Fornece fixture qtbot para simulacao de interacoes
- waitSignal permite aguardar sinais sem polling manual
- Configuracao qt_api=pyside6 em pytest.ini

**Notas**:
- Crashs aleatorios em PySide6: Issue #154 em qasync
- QApplication singleton: Reutilizar instancia entre testes
- pytest-qt nao tem suporte nativo a qasync, necessita fixtures customizadas

## 3. QAbstractTableModel para StoryTable

**Decisao**: Subclassear QAbstractTableModel com dados como lista de StoryOutputDTO.

**Racional**:
- QAbstractTableModel oferece renderizacao lazy (melhor performance para 500+ linhas)
- Separacao clara Model-View alinha com MVVM
- Suporta ordenacao nativa via Qt

**Thread-Safety**:
- QAbstractTableModel NAO e thread-safe
- Atualizacoes de dados DEVEM ocorrer na thread principal (GUI)
- ViewModels emitem signals que sao processados na thread principal

## 4. Padrao MVVM em PySide6

**Decisao**: ViewModels como QObject com Signals Qt para comunicacao reativa.

**Racional**:
- QObject permite usar signals/slots nativos do Qt
- Properties e signals permitem binding reativo
- Alinha com Constituicao XIX (MVVM)
- Testavel independente de Views

**Comunicacao**:
- View conecta aos signals do ViewModel (stories_changed, loading, error_occurred)
- View chama metodos do ViewModel via button.clicked.connect()

## 5. DI Container

**Decisao**: DIContainer como classe singleton que instancia todo o grafo de objetos.

**Racional**:
- Grafo de dependencias e estatico e conhecido
- Evita dependencia de biblioteca externa de DI
- Centraliza composicao na raiz (main) conforme Constituicao IV
- Facilita testes - pode mockar container ou componentes individuais

## 6. Tratamento de Erros

**Decisao**: ViewModels capturam excecoes e emitem signal error_occurred(str). Views exibem QMessageBox.

**Racional**:
- Mantem logica de tratamento no ViewModel (testavel)
- View apenas exibe mensagens (responsabilidade unica)
- Mensagens em PT-BR conforme Constituicao XV e XVI

**Mapeamento**:
- ValueError -> QMessageBox.warning com mensagem da excecao
- BacklogManagerException -> QMessageBox.warning com mensagem da excecao
- Outras exceptions -> QMessageBox.critical + log ERROR

## 7. Atalhos de Teclado

**Decisao**: Usar QShortcut para atalhos globais e QAction.setShortcut() para acoes de toolbar.

**Atalhos**:
- Ctrl+N: Nova historia
- Enter/F2: Editar historia selecionada
- Delete: Deletar historia (com confirmacao)
- Alt+Up: Mover prioridade para cima
- Alt+Down: Mover prioridade para baixo
- Ctrl+Shift+A: Executar alocacao automatica

## 8. Performance

**Decisao**: Lazy loading + async para manter responsividade.

**Estrategias**:
1. Cold Start: Inicializar apenas MainWindow e StoryTable no startup
2. Dialogos criados sob demanda
3. CRUD via async/await (nao bloqueiam UI)
4. Tabela atualizada via beginResetModel()/endResetModel()
5. Alocacao com progress indicator e botao desabilitado

## Resumo de Decisoes

| Topico | Decisao |
|--------|---------|
| Event Loop | qasync |
| Testes GUI | pytest-qt + fixtures customizadas |
| Table Model | QAbstractTableModel |
| MVVM | ViewModels como QObject com Signals |
| DI Container | Classe singleton manual |
| Tratamento de Erros | Signal error_occurred + QMessageBox |
| Atalhos | QShortcut + QAction |
| Performance | Lazy loading + async |
