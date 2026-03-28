"""Testes unitarios para StoryStatus."""

import pytest

from backlog_manager.domain.value_objects import StoryStatus


class TestStoryStatus:
    """Testes para o enum StoryStatus."""

    def test_has_five_states(self) -> None:
        """StoryStatus deve ter exatamente 5 estados."""
        assert len(StoryStatus) == 5

    def test_backlog_state_exists(self) -> None:
        """Estado BACKLOG deve existir."""
        assert StoryStatus.BACKLOG == "BACKLOG"

    def test_execucao_state_exists(self) -> None:
        """Estado EXECUCAO deve existir."""
        assert StoryStatus.EXECUCAO == "EXECUCAO"

    def test_testes_state_exists(self) -> None:
        """Estado TESTES deve existir."""
        assert StoryStatus.TESTES == "TESTES"

    def test_concluido_state_exists(self) -> None:
        """Estado CONCLUIDO deve existir."""
        assert StoryStatus.CONCLUIDO == "CONCLUIDO"

    def test_impedido_state_exists(self) -> None:
        """Estado IMPEDIDO deve existir."""
        assert StoryStatus.IMPEDIDO == "IMPEDIDO"

    def test_states_are_strings(self) -> None:
        """Todos os estados devem ser strings."""
        for status in StoryStatus:
            assert isinstance(status.value, str)

    def test_states_are_uppercase(self) -> None:
        """Todos os valores devem estar em maiusculas."""
        for status in StoryStatus:
            assert status.value == status.value.upper()

    def test_states_have_no_accents(self) -> None:
        """Nenhum estado deve ter acentos."""
        accented_chars = "áàãâéèêíìîóòõôúùûçÁÀÃÂÉÈÊÍÌÎÓÒÕÔÚÙÛÇ"
        for status in StoryStatus:
            for char in status.value:
                assert char not in accented_chars

    def test_create_from_string_value(self) -> None:
        """Deve ser possivel criar status a partir de string."""
        assert StoryStatus("BACKLOG") == StoryStatus.BACKLOG
        assert StoryStatus("EXECUCAO") == StoryStatus.EXECUCAO
        assert StoryStatus("TESTES") == StoryStatus.TESTES
        assert StoryStatus("CONCLUIDO") == StoryStatus.CONCLUIDO
        assert StoryStatus("IMPEDIDO") == StoryStatus.IMPEDIDO

    def test_invalid_status_raises_error(self) -> None:
        """Criar status com valor invalido deve lançar ValueError."""
        with pytest.raises(ValueError):
            StoryStatus("INVALID")

    def test_old_in_progress_does_not_exist(self) -> None:
        """Estado IN_PROGRESS antigo nao deve existir."""
        assert not hasattr(StoryStatus, "IN_PROGRESS")

    def test_old_blocked_does_not_exist(self) -> None:
        """Estado BLOCKED antigo nao deve existir."""
        assert not hasattr(StoryStatus, "BLOCKED")

    def test_old_done_does_not_exist(self) -> None:
        """Estado DONE antigo nao deve existir."""
        assert not hasattr(StoryStatus, "DONE")
