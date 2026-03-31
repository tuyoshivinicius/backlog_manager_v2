"""ViewModel para dialog de alocacao manual de desenvolvedores."""

from __future__ import annotations

import asyncio
import logging
from datetime import date
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, Signal

from backlog_manager.application.dto.allocation.get_developer_availability_dto import (
    GetDeveloperAvailabilityInputDTO,
    GetDeveloperAvailabilityOutputDTO,
)
from backlog_manager.application.dto.story import EditStoryInputDTO

if TYPE_CHECKING:
    from backlog_manager.presentation.container import DIContainer

logger = logging.getLogger(__name__)


class ManualAllocationDialogViewModel(QObject):
    """ViewModel para o ManualAllocationDialog.

    Gerencia carregamento de disponibilidade de desenvolvedores,
    selecao e confirmacao de alocacao manual.

    Signals:
        developers_loaded: Emitido quando dados de disponibilidade sao carregados.
        error_occurred: Emitido quando ocorre erro.
        allocation_confirmed: Emitido quando alocacao e confirmada com sucesso.
    """

    developers_loaded = Signal(object)  # GetDeveloperAvailabilityOutputDTO
    error_occurred = Signal(str)
    allocation_confirmed = Signal()

    def __init__(self, container: DIContainer, parent: QObject | None = None) -> None:
        """Inicializa o ViewModel.

        Args:
            container: Dependency injection container.
            parent: Optional parent QObject.
        """
        super().__init__(parent)
        self._container = container

        self._story_id: str = ""
        self._selected_developer_id: int | None = None
        self._original_start_date: date | None = None
        self._new_start_date: date | None = None
        self._new_end_date: date | None = None
        self._date_was_changed: bool = False
        self._availability_data: GetDeveloperAvailabilityOutputDTO | None = None

        logger.debug("ManualAllocationDialogViewModel initialized")

    @property
    def selected_developer_id(self) -> int | None:
        """ID do desenvolvedor selecionado."""
        return self._selected_developer_id

    @selected_developer_id.setter
    def selected_developer_id(self, value: int | None) -> None:
        """Define desenvolvedor selecionado."""
        self._selected_developer_id = value

    @property
    def new_start_date(self) -> date | None:
        """Nova data de inicio (se alterada)."""
        return self._new_start_date if self._date_was_changed else None

    @property
    def new_end_date(self) -> date | None:
        """Nova data de fim (se alterada)."""
        return self._new_end_date if self._date_was_changed else None

    def load_developers(
        self,
        story_id: str,
        candidate_start_date: date,
    ) -> None:
        """Carrega disponibilidade de desenvolvedores para a historia.

        Args:
            story_id: ID da historia alvo.
            candidate_start_date: Data de inicio candidata.
        """
        self._story_id = story_id
        if self._original_start_date is None:
            self._original_start_date = candidate_start_date

        asyncio.ensure_future(
            self._load_developers_async(story_id, candidate_start_date)
        )

    async def _load_developers_async(
        self, story_id: str, candidate_start_date: date
    ) -> None:
        """Carrega dados de disponibilidade de forma assincrona."""
        try:
            config_vm = self._container.config_dialog_viewmodel
            velocity = config_vm.velocity

            async with self._container.create_unit_of_work() as uow:
                use_case = self._container.create_get_developer_availability_use_case(
                    uow
                )
                input_dto = GetDeveloperAvailabilityInputDTO(
                    story_id=story_id,
                    candidate_start_date=candidate_start_date,
                    velocity=velocity,
                    allocation_criteria="LOAD_BALANCING",
                )
                result = await use_case.execute(input_dto)

            self._availability_data = result
            self._new_start_date = result.story_start_date
            self._new_end_date = result.story_end_date
            self.developers_loaded.emit(result)

        except Exception as e:
            logger.exception("Erro ao carregar disponibilidade de desenvolvedores")
            self.error_occurred.emit(str(e))

    def on_date_changed(self, new_date: date) -> None:
        """Recalcula disponibilidade ao alterar data de inicio.

        Args:
            new_date: Nova data de inicio selecionada.
        """
        if self._new_start_date == new_date:
            return

        self._date_was_changed = new_date != self._original_start_date
        self.load_developers(self._story_id, new_date)

    def confirm_allocation(self) -> None:
        """Confirma alocacao do desenvolvedor selecionado."""
        if self._selected_developer_id is None:
            return

        asyncio.ensure_future(self._confirm_allocation_async())

    async def _confirm_allocation_async(self) -> None:
        """Persiste alocacao de forma assincrona."""
        try:
            async with self._container.create_unit_of_work() as uow:
                use_case = self._container.create_edit_story_use_case(uow)

                edit_dto = EditStoryInputDTO(
                    story_id=self._story_id,
                    developer_id=self._selected_developer_id,
                )

                if (
                    self._date_was_changed
                    and self._new_start_date
                    and self._new_end_date
                ):
                    edit_dto = EditStoryInputDTO(
                        story_id=self._story_id,
                        developer_id=self._selected_developer_id,
                        start_date=self._new_start_date,
                        end_date=self._new_end_date,
                    )

                await use_case.execute(edit_dto)
                await uow.commit()

            self.allocation_confirmed.emit()
            logger.info(
                "Alocacao manual confirmada: story=%s, dev=%s",
                self._story_id,
                self._selected_developer_id,
            )

        except Exception as e:
            logger.exception("Erro ao confirmar alocacao manual")
            self.error_occurred.emit(str(e))

    def reset(self) -> None:
        """Reseta estado do viewmodel para reutilizacao."""
        self._story_id = ""
        self._selected_developer_id = None
        self._original_start_date = None
        self._new_start_date = None
        self._new_end_date = None
        self._date_was_changed = False
        self._availability_data = None
