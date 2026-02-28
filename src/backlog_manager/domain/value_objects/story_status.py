"""Story status value object."""

from enum import StrEnum


class StoryStatus(StrEnum):
    """Estados do workflow de uma historia.

    Transicoes validas:
        BACKLOG -> IN_PROGRESS -> DONE
        IN_PROGRESS -> BLOCKED -> IN_PROGRESS
    """

    BACKLOG = "BACKLOG"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    DONE = "DONE"
