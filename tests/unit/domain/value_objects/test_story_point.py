"""Testes unitarios para StoryPoint."""

import pytest

from backlog_manager.domain.value_objects import StoryPoint


class TestStoryPoint:
    """Testes para o enum StoryPoint."""

    def test_has_four_values(self) -> None:
        """StoryPoint deve ter exatamente 4 valores."""
        assert len(StoryPoint) == 4

    def test_small_value(self) -> None:
        """SMALL deve ter valor 3."""
        assert StoryPoint.SMALL == 3
        assert StoryPoint.SMALL.value == 3

    def test_medium_value(self) -> None:
        """MEDIUM deve ter valor 5."""
        assert StoryPoint.MEDIUM == 5
        assert StoryPoint.MEDIUM.value == 5

    def test_large_value(self) -> None:
        """LARGE deve ter valor 8."""
        assert StoryPoint.LARGE == 8
        assert StoryPoint.LARGE.value == 8

    def test_extra_large_value(self) -> None:
        """EXTRA_LARGE deve ter valor 13."""
        assert StoryPoint.EXTRA_LARGE == 13
        assert StoryPoint.EXTRA_LARGE.value == 13

    def test_all_values_are_fibonacci(self) -> None:
        """Todos os valores devem pertencer a sequencia Fibonacci."""
        fibonacci_values = {3, 5, 8, 13}
        for sp in StoryPoint:
            assert sp.value in fibonacci_values

    def test_create_from_integer(self) -> None:
        """Deve ser possivel criar StoryPoint a partir de inteiro valido."""
        assert StoryPoint(3) == StoryPoint.SMALL
        assert StoryPoint(5) == StoryPoint.MEDIUM
        assert StoryPoint(8) == StoryPoint.LARGE
        assert StoryPoint(13) == StoryPoint.EXTRA_LARGE

    def test_invalid_integer_raises_error(self) -> None:
        """Criar StoryPoint com valor invalido deve lancar ValueError."""
        invalid_values = [1, 2, 4, 6, 7, 10, 20, 21]
        for value in invalid_values:
            with pytest.raises(ValueError):
                StoryPoint(value)

    def test_negative_value_raises_error(self) -> None:
        """Criar StoryPoint com valor negativo deve lancar ValueError."""
        with pytest.raises(ValueError):
            StoryPoint(-3)

    def test_zero_value_raises_error(self) -> None:
        """Criar StoryPoint com valor zero deve lancar ValueError."""
        with pytest.raises(ValueError):
            StoryPoint(0)
