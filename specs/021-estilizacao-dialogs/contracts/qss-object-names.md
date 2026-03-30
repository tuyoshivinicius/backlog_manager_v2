# Contracts: QSS Object Names — Estilizacao de Dialogs

**Feature Branch**: `021-estilizacao-dialogs`
**Date**: 2026-03-29

---

## Convencao

- **Format**: kebab-case
- **Prefix**: nome do dialog ou semantica do componente
- **Selector QSS**: `#object-name` (ID selector)

---

## Object Names por Dialog

### StoryDialog

| Widget | objectName | Tipo Qt |
|--------|-----------|---------|
| Dialog | `story-dialog` | QDialog |
| Campo Componente | `story-component-field` | QLineEdit |
| Campo Nome | `story-name-field` | QLineEdit |
| Combo Story Points | `story-points-combo` | QComboBox |
| Combo Feature | `story-feature-combo` | QComboBox |
| Combo Desenvolvedor | `story-developer-combo` | QComboBox |
| Container Desenvolvedor | `story-developer-container` | QWidget |
| Botao Salvar | `story-save-button` | QPushButton |
| Botao Cancelar | `story-cancel-button` | QPushButton |

### DeveloperDialog

| Widget | objectName | Tipo Qt |
|--------|-----------|---------|
| Dialog | `developer-dialog` | QDialog |
| Lista | `developer-list` | QListWidget |
| Estado vazio | `developer-empty-state` | QLabel |
| Stacked container | `developer-stacked` | QStackedWidget |
| Botao Adicionar | `developer-add-button` | QPushButton |
| Botao Editar | `developer-edit-button` | QPushButton |
| Botao Remover | `developer-remove-button` | QPushButton |
| Botao Fechar | `developer-close-button` | QPushButton |

### FeatureDialog

| Widget | objectName | Tipo Qt |
|--------|-----------|---------|
| Dialog | `feature-dialog` | QDialog |
| Lista | `feature-list` | QListWidget |
| Estado vazio | `feature-empty-state` | QLabel |
| Stacked container | `feature-stacked` | QStackedWidget |

### ConfirmDeleteDialog

| Widget | objectName | Tipo Qt |
|--------|-----------|---------|
| Dialog | `confirm-delete-dialog` | QDialog |
| Icone alerta | `confirm-delete-icon` | QLabel |
| Texto principal | `confirm-delete-main-text` | QLabel |
| Texto complementar | `confirm-delete-detail-text` | QLabel |
| Botao confirmar | `confirm-delete-button` | QPushButton |
| Botao cancelar | `confirm-delete-cancel-button` | QPushButton |

### ProgressDialog

| Widget | objectName | Tipo Qt |
|--------|-----------|---------|
| Dialog | `progress-dialog` | QDialog |
| Barra de progresso | `progress-bar` | QProgressBar |
| Label mensagem | `progress-message` | QLabel |

### ResultDialog

| Widget | objectName | Tipo Qt |
|--------|-----------|---------|
| Dialog | `result-dialog` | QDialog |
| Label titulo | `result-title` | QLabel |
| Label detalhes | `result-details` | QLabel |
| Botao fechar | `result-close-button` | QPushButton |

---

## Object Names Transversais (Validacao)

| Widget | objectName | Tipo Qt | Uso |
|--------|-----------|---------|-----|
| Indicador obrigatorio | `required-indicator` | QLabel | Asterisco (*) vermelho |
| Label erro campo | `field-error-label` | QLabel | Mensagem de erro on-blur |
| Contagem caracteres | `field-char-count` | QLabel | "N/MAX" |

---

## QSS Property Selectors (Dynamic Styling)

| Selector | Property | Values | Uso |
|----------|----------|--------|-----|
| `QLineEdit[error="true"]` | error | true/false | Borda vermelha em campo invalido |
| `QLabel#field-char-count[warning="true"]` | warning | true/false | Cor de alerta quando >= 90% |
| `QPushButton#confirm-delete-button` | — | — | Fundo vermelho, texto branco |
| `QPushButton#story-save-button:disabled` | — | — | Fundo cinza quando desabilitado |
