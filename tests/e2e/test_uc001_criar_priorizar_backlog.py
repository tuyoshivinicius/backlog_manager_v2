"""E2E tests for UC-001: Criar e Priorizar Backlog.

Tests the main story management flows including creation,
validation, and priority manipulation.
"""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt

from backlog_manager.application.dto.story import CreateStoryInputDTO

pytestmark = [pytest.mark.e2e]


class TestUC001CriarHistoria:
    """Tests for story creation flow (FR-030)."""

    @pytest.mark.asyncio
    async def test_criar_historia_com_sucesso(
        self, e2e_main_window, e2e_app, qasync_loop
    ):
        """Test successful story creation via ViewModel.

        FR-030: Create story with valid data should succeed.
        """
        viewmodel = e2e_main_window.viewmodel

        # Create story
        dto = CreateStoryInputDTO(
            component="TEST",
            name="Historia de Teste E2E",
            story_points=5,
            feature_id=None,
        )

        story = await viewmodel.create_story(dto)

        # Verify story was created
        assert story is not None
        assert story.id == "TEST-001"
        assert story.name == "Historia de Teste E2E"
        assert story.story_points == 5
        assert story.status == "BACKLOG"
        assert story.priority == 1

        # Reload to verify story appears in table
        await viewmodel.load_stories()
        assert len(viewmodel.stories) == 1
        assert viewmodel.stories[0].id == "TEST-001"

    @pytest.mark.asyncio
    async def test_criar_multiplas_historias_prioridade_sequencial(
        self, e2e_main_window, e2e_app, qasync_loop
    ):
        """Test that multiple stories get sequential priorities.

        FR-030: Stories should be assigned sequential priorities.
        """
        viewmodel = e2e_main_window.viewmodel

        # Create multiple stories
        for i in range(1, 6):
            dto = CreateStoryInputDTO(
                component="SEQ",
                name=f"Historia {i}",
                story_points=5,
            )
            await viewmodel.create_story(dto)

        # Reload and verify priorities
        await viewmodel.load_stories()
        stories = viewmodel.stories
        assert len(stories) == 5
        for i, story in enumerate(stories):
            assert story.priority == i + 1


class TestUC001RejeitarSPInvalido:
    """Tests for story point validation (FR-031)."""

    @pytest.mark.asyncio
    async def test_rejeitar_sp_invalido_valor_fora_fibonacci(
        self, e2e_main_window, e2e_app, qasync_loop, qtbot
    ):
        """Test that invalid story points are rejected.

        FR-031: Story points must be 3, 5, 8, or 13.
        """
        from pydantic import ValidationError

        # Try to create DTO with invalid SP (2 is not Fibonacci)
        # Pydantic validation should reject it at DTO creation
        error_raised = False
        try:
            dto = CreateStoryInputDTO(
                component="INV",
                name="Historia Invalida",
                story_points=2,  # Invalid!
            )
        except ValidationError as e:
            error_raised = True
            assert "story_points" in str(e).lower() or "story points" in str(e).lower()

        assert error_raised, "Invalid story points should be rejected by DTO validation"

    @pytest.mark.asyncio
    async def test_aceitar_sp_validos(self, e2e_main_window, e2e_app, qasync_loop):
        """Test that valid story points are accepted.

        FR-031: Valid story points: 3, 5, 8, 13.
        """
        viewmodel = e2e_main_window.viewmodel
        valid_sps = [3, 5, 8, 13]

        for sp in valid_sps:
            dto = CreateStoryInputDTO(
                component="VAL",
                name=f"Historia SP {sp}",
                story_points=sp,
            )
            story = await viewmodel.create_story(dto)
            assert story is not None
            assert story.story_points == sp


class TestUC001AlterarPrioridade:
    """Tests for priority manipulation (FR-032)."""

    @pytest.mark.asyncio
    async def test_alterar_prioridade_mover_cima(
        self, e2e_main_window, e2e_app, qasync_loop
    ):
        """Test moving story priority up.

        FR-032: Moving priority up should swap with previous story.
        """
        viewmodel = e2e_main_window.viewmodel

        # Create stories
        for i in range(1, 4):
            dto = CreateStoryInputDTO(
                component="PRIO",
                name=f"Historia {i}",
                story_points=5,
            )
            await viewmodel.create_story(dto)

        # Move second story up
        await viewmodel.move_priority_up("PRIO-002")

        # Reload and verify priorities swapped
        await viewmodel.load_stories()
        stories = viewmodel.stories
        assert stories[0].id == "PRIO-002"  # Was second, now first
        assert stories[1].id == "PRIO-001"  # Was first, now second
        assert stories[2].id == "PRIO-003"  # Unchanged

    @pytest.mark.asyncio
    async def test_alterar_prioridade_mover_baixo(
        self, e2e_main_window, e2e_app, qasync_loop
    ):
        """Test moving story priority down.

        FR-032: Moving priority down should swap with next story.
        """
        viewmodel = e2e_main_window.viewmodel

        # Create stories
        for i in range(1, 4):
            dto = CreateStoryInputDTO(
                component="PRIO",
                name=f"Historia {i}",
                story_points=5,
            )
            await viewmodel.create_story(dto)

        # Move first story down
        await viewmodel.move_priority_down("PRIO-001")

        # Reload and verify priorities swapped
        await viewmodel.load_stories()
        stories = viewmodel.stories
        assert stories[0].id == "PRIO-002"  # Was second, now first
        assert stories[1].id == "PRIO-001"  # Was first, now second
        assert stories[2].id == "PRIO-003"  # Unchanged

    @pytest.mark.asyncio
    async def test_mover_primeira_historia_cima_sem_efeito(
        self, e2e_main_window, e2e_app, qasync_loop
    ):
        """Test that moving first story up has no effect.

        FR-032: First story cannot move up.
        """
        viewmodel = e2e_main_window.viewmodel

        # Create stories
        dto = CreateStoryInputDTO(
            component="EDGE",
            name="Primeira Historia",
            story_points=5,
        )
        await viewmodel.create_story(dto)

        # Try to move first story up
        result = await viewmodel.move_priority_up("EDGE-001")

        # Reload - should succeed but have no effect (or fail gracefully)
        await viewmodel.load_stories()
        stories = viewmodel.stories
        assert stories[0].id == "EDGE-001"
        assert stories[0].priority == 1

    @pytest.mark.asyncio
    async def test_mover_ultima_historia_baixo_sem_efeito(
        self, e2e_main_window, e2e_app, qasync_loop
    ):
        """Test that moving last story down has no effect.

        FR-032: Last story cannot move down.
        """
        viewmodel = e2e_main_window.viewmodel

        # Create two stories
        for i in range(1, 3):
            dto = CreateStoryInputDTO(
                component="EDGE",
                name=f"Historia {i}",
                story_points=5,
            )
            await viewmodel.create_story(dto)

        # Try to move last story down
        result = await viewmodel.move_priority_down("EDGE-002")

        # Reload - should succeed but have no effect (or fail gracefully)
        await viewmodel.load_stories()
        stories = viewmodel.stories
        assert stories[1].id == "EDGE-002"
        assert stories[1].priority == 2


class TestUC001DeleteStory:
    """Tests for story deletion."""

    @pytest.mark.asyncio
    async def test_deletar_historia_com_sucesso(
        self, e2e_main_window, e2e_app, qasync_loop
    ):
        """Test successful story deletion."""
        viewmodel = e2e_main_window.viewmodel

        # Create story
        dto = CreateStoryInputDTO(
            component="DEL",
            name="Historia para Deletar",
            story_points=5,
        )
        await viewmodel.create_story(dto)
        await viewmodel.load_stories()
        assert len(viewmodel.stories) == 1

        # Delete story
        result = await viewmodel.delete_story("DEL-001")

        await viewmodel.load_stories()
        assert result is True
        assert len(viewmodel.stories) == 0

    @pytest.mark.asyncio
    async def test_deletar_historia_reordena_prioridades(
        self, e2e_main_window, e2e_app, qasync_loop
    ):
        """Test that deleting a story reorders priorities correctly."""
        viewmodel = e2e_main_window.viewmodel

        # Create stories
        for i in range(1, 4):
            dto = CreateStoryInputDTO(
                component="REORD",
                name=f"Historia {i}",
                story_points=5,
            )
            await viewmodel.create_story(dto)

        # Delete middle story
        await viewmodel.delete_story("REORD-002")

        # Reload and verify remaining stories
        await viewmodel.load_stories()
        stories = viewmodel.stories
        assert len(stories) == 2
        # Priorities should still be sequential
        assert stories[0].priority < stories[1].priority
