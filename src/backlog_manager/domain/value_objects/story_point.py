"""Story point value object."""

from enum import IntEnum


class StoryPoint(IntEnum):
    """Escala Fibonacci para estimativa de historias.

    Valores permitidos: 3 (pequena), 5 (media), 8 (grande), 13 (muito grande).
    """

    SMALL = 3
    MEDIUM = 5
    LARGE = 8
    EXTRA_LARGE = 13
