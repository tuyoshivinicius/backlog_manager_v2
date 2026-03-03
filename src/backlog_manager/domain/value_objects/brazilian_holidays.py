"""Brazilian national holidays for 2026-2028.

Contains a frozenset of all Brazilian national holiday dates for 2026-2028.
This is used by SchedulingService to calculate workdays and schedules.
"""

from __future__ import annotations

from datetime import date

# Brazilian national holidays for 2026-2028
# Source: SRS Apendice A - EP-006 Calculo de Cronograma
BRAZILIAN_HOLIDAYS_2026_2028: frozenset[date] = frozenset(
    [
        # 2026
        date(2026, 1, 1),  # Confraternizacao Universal
        date(2026, 2, 16),  # Carnaval (segunda)
        date(2026, 2, 17),  # Carnaval (terca)
        date(2026, 4, 3),  # Sexta-feira Santa
        date(2026, 4, 21),  # Tiradentes
        date(2026, 5, 1),  # Dia do Trabalho
        date(2026, 6, 4),  # Corpus Christi
        date(2026, 9, 7),  # Independencia do Brasil
        date(2026, 10, 12),  # Nossa Senhora Aparecida
        date(2026, 11, 2),  # Finados
        date(2026, 11, 15),  # Proclamacao da Republica
        date(2026, 11, 20),  # Consciencia Negra
        date(2026, 12, 25),  # Natal
        # 2027
        date(2027, 1, 1),  # Confraternizacao Universal
        date(2027, 2, 8),  # Carnaval (segunda)
        date(2027, 2, 9),  # Carnaval (terca)
        date(2027, 3, 26),  # Sexta-feira Santa
        date(2027, 4, 21),  # Tiradentes
        date(2027, 5, 1),  # Dia do Trabalho
        date(2027, 5, 27),  # Corpus Christi
        date(2027, 9, 7),  # Independencia do Brasil
        date(2027, 10, 12),  # Nossa Senhora Aparecida
        date(2027, 11, 2),  # Finados
        date(2027, 11, 15),  # Proclamacao da Republica
        date(2027, 11, 20),  # Consciencia Negra
        date(2027, 12, 25),  # Natal
        # 2028
        date(2028, 1, 1),  # Confraternizacao Universal
        date(2028, 2, 28),  # Carnaval (segunda)
        date(2028, 2, 29),  # Carnaval (terca)
        date(2028, 4, 14),  # Sexta-feira Santa
        date(2028, 4, 21),  # Tiradentes
        date(2028, 5, 1),  # Dia do Trabalho
        date(2028, 6, 15),  # Corpus Christi
        date(2028, 9, 7),  # Independencia do Brasil
        date(2028, 10, 12),  # Nossa Senhora Aparecida
        date(2028, 11, 2),  # Finados
        date(2028, 11, 15),  # Proclamacao da Republica
        date(2028, 11, 20),  # Consciencia Negra
        date(2028, 12, 25),  # Natal
    ]
)


def get_holidays_for_year(year: int) -> frozenset[date]:
    """Return Brazilian holidays for a specific year.

    Args:
        year: The year to get holidays for (2026, 2027, or 2028).

    Returns:
        A frozenset of date objects for the holidays in that year.
        Returns an empty frozenset for years outside 2026-2028.

    Example:
        >>> holidays_2026 = get_holidays_for_year(2026)
        >>> len(holidays_2026)
        13
        >>> date(2026, 4, 21) in holidays_2026  # Tiradentes
        True
    """
    return frozenset(d for d in BRAZILIAN_HOLIDAYS_2026_2028 if d.year == year)
