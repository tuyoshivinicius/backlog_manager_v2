"""Planning domain exceptions."""

from backlog_manager.domain.exceptions.base import BacklogManagerException


class PlanningException(BacklogManagerException):
    """Excecao base para erros relacionados a planejamentos."""


class DuplicatePlanningNameException(PlanningException):
    """Excecao para nome de planejamento duplicado."""

    def __init__(self, name: str) -> None:
        """Initialize exception.

        Args:
            name: Nome duplicado do planejamento.
        """
        self.name = name
        super().__init__(f"Ja existe um planejamento com o nome '{name}'")


class ActivePlanningDeletionException(PlanningException):
    """Excecao para tentativa de excluir planejamento ativo."""

    def __init__(self, planning_id: int) -> None:
        """Initialize exception.

        Args:
            planning_id: ID do planejamento ativo.
        """
        self.planning_id = planning_id
        super().__init__(
            "Nao e possivel excluir o planejamento ativo. "
            "Ative outro planejamento primeiro."
        )
