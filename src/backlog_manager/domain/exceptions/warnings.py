"""Backlog Manager warnings."""

from __future__ import annotations


class BacklogWarning(Warning):
    """Warning base para situacoes nao-bloqueantes do Backlog Manager.

    Warnings nao interrompem a execucao, mas sinalizam situacoes
    que merecem atencao do usuario.

    Example:
        >>> import warnings
        >>> warnings.warn("Situacao de atencao", BacklogWarning)
    """


class DeadlockWarning(BacklogWarning):
    """Deadlock detectado na alocacao de historias.

    Emitido quando o algoritmo de alocacao detecta que nenhum
    progresso e possivel em uma iteracao, ou quando o limite
    maximo de iteracoes e atingido.

    Attributes:
        wave: Wave onde o deadlock foi detectado.
        blocked_stories: Lista de IDs de historias bloqueadas.
        max_iterations_reached: True se o limite de iteracoes foi atingido.
    """

    def __init__(
        self,
        wave: int,
        blocked_stories: list[str],
        max_iterations_reached: bool = False,
    ) -> None:
        """Initialize warning.

        Args:
            wave: Wave onde o deadlock foi detectado.
            blocked_stories: Lista de IDs de historias bloqueadas.
            max_iterations_reached: True se o limite de iteracoes foi atingido.
        """
        self.wave = wave
        self.blocked_stories = blocked_stories
        self.max_iterations_reached = max_iterations_reached
        if max_iterations_reached:
            message = (
                f"Limite de iteracoes atingido na wave {wave}: "
                f"{len(blocked_stories)} historia(s) nao alocada(s)"
            )
        else:
            message = (
                f"Deadlock detectado na wave {wave}: "
                f"{len(blocked_stories)} historia(s) bloqueada(s)"
            )
        super().__init__(message)


class IdlenessWarning(BacklogWarning):
    """Ociosidade detectada para um desenvolvedor.

    Emitido quando um desenvolvedor fica ocioso por mais dias
    do que o configurado.

    Attributes:
        developer_id: ID do desenvolvedor ocioso.
        developer_name: Nome do desenvolvedor.
        idle_days: Numero de dias ociosos.
        wave: Wave onde a ociosidade foi detectada.
    """

    def __init__(
        self,
        developer_id: int,
        developer_name: str,
        idle_days: int,
        wave: int,
    ) -> None:
        """Initialize warning.

        Args:
            developer_id: ID do desenvolvedor ocioso.
            developer_name: Nome do desenvolvedor.
            idle_days: Numero de dias ociosos.
            wave: Wave onde a ociosidade foi detectada.
        """
        self.developer_id = developer_id
        self.developer_name = developer_name
        self.idle_days = idle_days
        self.wave = wave
        message = (
            f"Desenvolvedor '{developer_name}' ocioso por {idle_days} dias "
            f"na wave {wave}"
        )
        super().__init__(message)


class BetweenWavesIdlenessInfo(BacklogWarning):
    """Informativo de ociosidade entre waves.

    Emitido para informar que houve ociosidade na transicao
    entre waves (situacao esperada e nao problematica).

    Attributes:
        developer_id: ID do desenvolvedor.
        developer_name: Nome do desenvolvedor.
        idle_days: Numero de dias ociosos.
        from_wave: Wave de origem.
        to_wave: Wave de destino.
    """

    def __init__(
        self,
        developer_id: int,
        developer_name: str,
        idle_days: int,
        from_wave: int,
        to_wave: int,
    ) -> None:
        """Initialize warning.

        Args:
            developer_id: ID do desenvolvedor.
            developer_name: Nome do desenvolvedor.
            idle_days: Numero de dias ociosos.
            from_wave: Wave de origem.
            to_wave: Wave de destino.
        """
        self.developer_id = developer_id
        self.developer_name = developer_name
        self.idle_days = idle_days
        self.from_wave = from_wave
        self.to_wave = to_wave
        message = (
            f"Desenvolvedor '{developer_name}' ocioso por {idle_days} dias "
            f"entre wave {from_wave} e wave {to_wave} (esperado)"
        )
        super().__init__(message)
