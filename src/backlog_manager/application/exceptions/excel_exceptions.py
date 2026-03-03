"""Excel-specific exceptions for import/export operations."""

from backlog_manager.domain.exceptions.base import BacklogManagerException


class ExcelException(BacklogManagerException):
    """Excecao base para operacoes Excel.

    Todas as excecoes relacionadas a operacoes de import/export Excel
    herdam desta classe.
    """


class ExcelFileNotFoundException(ExcelException):
    """Arquivo Excel nao encontrado.

    Lancada quando o arquivo especificado para import nao existe
    no sistema de arquivos.
    """


class ExcelFileCorruptedException(ExcelException):
    """Arquivo Excel corrompido ou formato invalido.

    Lancada quando o arquivo existe mas nao pode ser lido
    como um arquivo Excel valido (formato .xlsx).
    """


class ExcelMissingHeaderException(ExcelException):
    """Coluna obrigatoria ausente no arquivo Excel.

    Lancada quando o arquivo Excel nao contem uma ou mais
    colunas obrigatorias na primeira linha (header).
    """


class ExcelCycleDetectedException(ExcelException):
    """Ciclo de dependencia detectado no arquivo importado.

    Lancada quando as dependencias definidas no arquivo Excel
    formam um ciclo, o que e invalido para o sistema.
    """


class ExcelPermissionException(ExcelException):
    """Sem permissao para ler/escrever arquivo Excel.

    Lancada quando o sistema nao tem permissao para acessar
    o arquivo ou diretorio especificado.
    """
