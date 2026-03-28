"""Base exception for Backlog Manager."""


class BacklogManagerException(Exception):
    """Excecao base para todos os erros do Backlog Manager.

    Todas as excecoes customizadas do sistema herdam desta classe,
    permitindo catch generico para tratamento uniforme de erros.

    Example:
        >>> try:
        ...     # operacao que pode falhar
        ...     pass
        ... except BacklogManagerException as e:
        ...     print(f"Erro: {e}")
    """
