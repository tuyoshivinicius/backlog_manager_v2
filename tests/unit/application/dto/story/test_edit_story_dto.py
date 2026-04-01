"""Unit tests for EditStoryInputDTO validators."""

from __future__ import annotations

import pytest
from backlog_manager.application.dto.story.edit_story_dto import EditStoryInputDTO
from pydantic import ValidationError


@pytest.mark.unit
class TestEditStoryInputDTONameValidator:
    """Tests for the name field validator."""

    def test_name_none_is_accepted(self):
        """Name=None should pass validation and remain None (line 31)."""
        dto = EditStoryInputDTO(story_id="S-001", name=None)
        assert dto.name is None

    def test_name_not_provided_defaults_to_none(self):
        """Omitting name should default to None."""
        dto = EditStoryInputDTO(story_id="S-001")
        assert dto.name is None

    def test_name_empty_string_raises(self):
        """Empty string name should raise ValueError (line 33)."""
        with pytest.raises(ValidationError, match="Nome nao pode ser vazio"):
            EditStoryInputDTO(story_id="S-001", name="")

    def test_name_whitespace_only_raises(self):
        """Whitespace-only name should raise ValueError (line 33)."""
        with pytest.raises(ValidationError, match="Nome nao pode ser vazio"):
            EditStoryInputDTO(story_id="S-001", name="   ")

    def test_name_exceeds_200_chars_raises(self):
        """Name longer than 200 characters should raise ValueError (line 35)."""
        long_name = "a" * 201
        with pytest.raises(
            ValidationError, match="Nome nao pode exceder 200 caracteres"
        ):
            EditStoryInputDTO(story_id="S-001", name=long_name)

    def test_name_exactly_200_chars_accepted(self):
        """Name with exactly 200 characters should be accepted."""
        name = "a" * 200
        dto = EditStoryInputDTO(story_id="S-001", name=name)
        assert dto.name == name

    def test_name_is_stripped(self):
        """Name with surrounding whitespace should be stripped."""
        dto = EditStoryInputDTO(story_id="S-001", name="  Test Story  ")
        assert dto.name == "Test Story"


@pytest.mark.unit
class TestEditStoryInputDTOStoryPointsValidator:
    """Tests for the story_points field validator."""

    def test_story_points_none_is_accepted(self):
        """story_points=None should pass validation (line 43)."""
        dto = EditStoryInputDTO(story_id="S-001", story_points=None)
        assert dto.story_points is None

    def test_story_points_not_provided_defaults_to_none(self):
        """Omitting story_points should default to None."""
        dto = EditStoryInputDTO(story_id="S-001")
        assert dto.story_points is None

    def test_story_points_invalid_value_raises(self):
        """Non-Fibonacci story points should raise ValueError (line 46)."""
        with pytest.raises(ValidationError, match="Story points deve ser um de"):
            EditStoryInputDTO(story_id="S-001", story_points=7)

    def test_story_points_zero_raises(self):
        """Zero story points should raise ValueError (line 46)."""
        with pytest.raises(ValidationError, match="Story points deve ser um de"):
            EditStoryInputDTO(story_id="S-001", story_points=0)

    def test_story_points_negative_raises(self):
        """Negative story points should raise ValueError (line 46)."""
        with pytest.raises(ValidationError, match="Story points deve ser um de"):
            EditStoryInputDTO(story_id="S-001", story_points=-1)

    @pytest.mark.parametrize("points", [3, 5, 8, 13])
    def test_story_points_valid_fibonacci_accepted(self, points: int):
        """All valid Fibonacci values should be accepted."""
        dto = EditStoryInputDTO(story_id="S-001", story_points=points)
        assert dto.story_points == points


@pytest.mark.unit
class TestEditStoryInputDTOStatusValidator:
    """Tests for the status field validator."""

    def test_status_none_is_accepted(self):
        """status=None should pass validation (line 54)."""
        dto = EditStoryInputDTO(story_id="S-001", status=None)
        assert dto.status is None

    def test_status_not_provided_defaults_to_none(self):
        """Omitting status should default to None."""
        dto = EditStoryInputDTO(story_id="S-001")
        assert dto.status is None

    def test_status_invalid_value_raises(self):
        """Invalid status should raise ValueError (line 57)."""
        with pytest.raises(ValidationError, match="Status deve ser um de"):
            EditStoryInputDTO(story_id="S-001", status="INVALIDO")

    def test_status_random_string_raises(self):
        """Random string status should raise ValueError (line 57)."""
        with pytest.raises(ValidationError, match="Status deve ser um de"):
            EditStoryInputDTO(story_id="S-001", status="foo")

    @pytest.mark.parametrize(
        "status",
        ["BACKLOG", "EXECUCAO", "TESTES", "CONCLUIDO", "IMPEDIDO"],
    )
    def test_status_valid_values_accepted(self, status: str):
        """All valid status values should be accepted."""
        dto = EditStoryInputDTO(story_id="S-001", status=status)
        assert dto.status == status

    def test_status_lowercase_is_uppercased(self):
        """Lowercase status should be converted to uppercase."""
        dto = EditStoryInputDTO(story_id="S-001", status="backlog")
        assert dto.status == "BACKLOG"

    def test_status_mixed_case_is_uppercased(self):
        """Mixed case status should be converted to uppercase."""
        dto = EditStoryInputDTO(story_id="S-001", status="Execucao")
        assert dto.status == "EXECUCAO"


@pytest.mark.unit
class TestEditStoryInputDTODurationValidator:
    """Tests for the duration field validator."""

    def test_duration_none_is_accepted(self):
        """duration=None should pass validation (line 66 return branch)."""
        dto = EditStoryInputDTO(story_id="S-001", duration=None)
        assert dto.duration is None

    def test_duration_negative_raises(self):
        """Negative duration should raise ValueError (lines 64-65)."""
        with pytest.raises(ValidationError, match="Duracao deve ser >= 0"):
            EditStoryInputDTO(story_id="S-001", duration=-1)

    def test_duration_zero_accepted(self):
        """Zero duration should be accepted (line 66)."""
        dto = EditStoryInputDTO(story_id="S-001", duration=0)
        assert dto.duration == 0

    def test_duration_positive_accepted(self):
        """Positive duration should be accepted (line 66)."""
        dto = EditStoryInputDTO(story_id="S-001", duration=5)
        assert dto.duration == 5
