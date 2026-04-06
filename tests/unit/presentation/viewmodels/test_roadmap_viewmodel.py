"""Headless tests for RoadmapViewModel."""

from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.headless_mocks import create_pyside6_mocks

_mock_qt_core, _pyside6_mocks = create_pyside6_mocks()

with patch.dict("sys.modules", _pyside6_mocks):
    from backlog_manager.presentation.viewmodels.roadmap_viewmodel import (
        RoadmapData,
        RoadmapFilters,
        RoadmapGroup,
        RoadmapViewModel,
    )

from backlog_manager.application.dto.feature.feature_output_dto import FeatureOutputDTO
from backlog_manager.application.dto.feature.list_features_dto import (
    ListFeaturesOutputDTO,
)
from backlog_manager.application.dto.story.story_output_dto import StoryOutputDTO

# --- Fixtures ---


def _make_story(
    id: str = "COMP-001",
    component: str = "Backend",
    name: str = "Story 1",
    story_points: int = 5,
    priority: int = 1,
    status: str = "BACKLOG",
    duration: int | None = 5,
    start_date: date | None = date(2026, 1, 15),
    end_date: date | None = date(2026, 1, 20),
    developer_id: int | None = 1,
    feature_id: int | None = 1,
    developer_name: str | None = "Dev A",
    feature_name: str | None = "Feature A",
    wave: int = 1,
    dependency_ids: list[str] | None = None,
) -> StoryOutputDTO:
    return StoryOutputDTO(
        id=id,
        component=component,
        name=name,
        story_points=story_points,
        priority=priority,
        status=status,
        duration=duration,
        start_date=start_date,
        end_date=end_date,
        developer_id=developer_id,
        feature_id=feature_id,
        developer_name=developer_name,
        feature_name=feature_name,
        wave=wave,
        dependency_ids=dependency_ids or [],
    )


def _make_feature(
    id: int = 1, name: str = "Feature A", wave: int = 1
) -> FeatureOutputDTO:
    return FeatureOutputDTO(id=id, name=name, wave=wave)


@pytest.fixture
def stories() -> list[StoryOutputDTO]:
    return [
        _make_story(
            id="BACK-001",
            name="Story 1",
            status="CONCLUIDO",
            start_date=date(2026, 1, 15),
            end_date=date(2026, 1, 20),
            feature_id=1,
            feature_name="Feature A",
            wave=1,
            component="Backend",
            developer_name="Dev A",
        ),
        _make_story(
            id="BACK-002",
            name="Story 2",
            status="EXECUCAO",
            start_date=date(2026, 1, 20),
            end_date=date(2026, 2, 10),
            feature_id=1,
            feature_name="Feature A",
            wave=1,
            component="Backend",
            developer_name="Dev B",
        ),
        _make_story(
            id="FRONT-001",
            name="Story 3",
            status="BACKLOG",
            component="Frontend",
            start_date=date(2026, 2, 1),
            end_date=date(2026, 2, 15),
            feature_id=2,
            feature_name="Feature B",
            wave=2,
            developer_name="Dev A",
        ),
    ]


@pytest.fixture
def features() -> list[FeatureOutputDTO]:
    return [
        _make_feature(id=1, name="Feature A", wave=1),
        _make_feature(id=2, name="Feature B", wave=2),
    ]


@pytest.fixture
def mock_list_stories_uc(stories):
    uc = AsyncMock()
    uc.execute.return_value = stories
    return uc


@pytest.fixture
def mock_list_features_uc(features):
    uc = AsyncMock()
    uc.execute.return_value = ListFeaturesOutputDTO(features=features)
    return uc


def _make_mock_container(mock_list_stories_uc, mock_list_features_uc):
    """Create a mock container that provides UoW as async context manager."""
    container = MagicMock()
    mock_uow = AsyncMock()
    mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
    mock_uow.__aexit__ = AsyncMock(return_value=False)
    container.create_unit_of_work.return_value = mock_uow
    container.create_list_stories_use_case.return_value = mock_list_stories_uc
    container.create_list_features_use_case.return_value = mock_list_features_uc
    return container


@pytest.fixture
def mock_container(mock_list_stories_uc, mock_list_features_uc):
    return _make_mock_container(mock_list_stories_uc, mock_list_features_uc)


@pytest.fixture
def viewmodel(mock_container):
    return RoadmapViewModel(mock_container)


# --- T011: Tests for RoadmapFilters ---


class TestRoadmapFilters:
    def test_is_active_default_false(self):
        f = RoadmapFilters()
        assert f.is_active is False

    def test_is_active_feature(self):
        f = RoadmapFilters(feature="Feature A")
        assert f.is_active is True

    def test_is_active_developer(self):
        f = RoadmapFilters(developer="Dev A")
        assert f.is_active is True

    def test_is_active_component(self):
        f = RoadmapFilters(component="Backend")
        assert f.is_active is True

    def test_is_active_search_text(self):
        f = RoadmapFilters(search_text="story")
        assert f.is_active is True

    def test_is_active_empty_search_text(self):
        f = RoadmapFilters(search_text="   ")
        assert f.is_active is False

    def test_matches_no_filters(self):
        story = _make_story()
        f = RoadmapFilters()
        assert f.matches(story) is True

    def test_matches_feature_pass(self):
        story = _make_story(feature_name="Feature A")
        f = RoadmapFilters(feature="Feature A")
        assert f.matches(story) is True

    def test_matches_feature_fail(self):
        story = _make_story(feature_name="Feature B")
        f = RoadmapFilters(feature="Feature A")
        assert f.matches(story) is False

    def test_matches_feature_none_story(self):
        story = _make_story(feature_name=None)
        f = RoadmapFilters(feature="Feature A")
        assert f.matches(story) is False

    def test_matches_developer_pass(self):
        story = _make_story(developer_name="Dev A")
        f = RoadmapFilters(developer="Dev A")
        assert f.matches(story) is True

    def test_matches_developer_fail(self):
        story = _make_story(developer_name="Dev B")
        f = RoadmapFilters(developer="Dev A")
        assert f.matches(story) is False

    def test_matches_component_pass(self):
        story = _make_story(component="Backend")
        f = RoadmapFilters(component="Backend")
        assert f.matches(story) is True

    def test_matches_component_fail(self):
        story = _make_story(component="Frontend")
        f = RoadmapFilters(component="Backend")
        assert f.matches(story) is False

    def test_matches_search_text_case_insensitive(self):
        story = _make_story(name="My Important Story")
        f = RoadmapFilters(search_text="important")
        assert f.matches(story) is True

    def test_matches_search_text_fail(self):
        story = _make_story(name="Story 1")
        f = RoadmapFilters(search_text="nonexistent")
        assert f.matches(story) is False

    def test_matches_and_logic_all_pass(self):
        story = _make_story(
            feature_name="Feature A", component="Backend", developer_name="Dev A"
        )
        f = RoadmapFilters(feature="Feature A", component="Backend", developer="Dev A")
        assert f.matches(story) is True

    def test_matches_and_logic_one_fails(self):
        story = _make_story(
            feature_name="Feature A", component="Frontend", developer_name="Dev A"
        )
        f = RoadmapFilters(feature="Feature A", component="Backend", developer="Dev A")
        assert f.matches(story) is False

    def test_matches_developer_none_fails(self):
        story = _make_story(developer_name=None)
        f = RoadmapFilters(developer="Dev A")
        assert f.matches(story) is False


# --- T012: Tests for RoadmapGroup properties ---


class TestRoadmapGroup:
    def test_completion_percent_empty(self):
        group = RoadmapGroup(name="Empty")
        assert group.completion_percent == 0.0

    def test_completion_percent_all_done(self):
        group = RoadmapGroup(
            name="Done",
            stories=[
                _make_story(id="A", status="CONCLUIDO"),
                _make_story(id="B", status="CONCLUIDO"),
            ],
        )
        assert group.completion_percent == 100.0

    def test_completion_percent_partial(self):
        group = RoadmapGroup(
            name="Mix",
            stories=[
                _make_story(id="A", status="CONCLUIDO"),
                _make_story(id="B", status="EXECUCAO"),
                _make_story(id="C", status="BACKLOG"),
            ],
        )
        assert abs(group.completion_percent - 33.33) < 0.1

    def test_has_scheduled_stories_true(self):
        group = RoadmapGroup(
            name="G",
            stories=[
                _make_story(start_date=date(2026, 1, 1), end_date=date(2026, 1, 5))
            ],
        )
        assert group.has_scheduled_stories is True

    def test_has_scheduled_stories_false(self):
        group = RoadmapGroup(
            name="G",
            stories=[_make_story(start_date=None, end_date=None)],
        )
        assert group.has_scheduled_stories is False

    def test_min_date(self):
        group = RoadmapGroup(
            name="G",
            stories=[
                _make_story(id="A", start_date=date(2026, 1, 10)),
                _make_story(id="B", start_date=date(2026, 1, 5)),
                _make_story(id="C", start_date=None),
            ],
        )
        assert group.min_date == date(2026, 1, 5)

    def test_min_date_no_dates(self):
        group = RoadmapGroup(
            name="G",
            stories=[_make_story(start_date=None)],
        )
        assert group.min_date is None

    def test_max_date(self):
        group = RoadmapGroup(
            name="G",
            stories=[
                _make_story(id="A", end_date=date(2026, 2, 10)),
                _make_story(id="B", end_date=date(2026, 3, 15)),
                _make_story(id="C", end_date=None),
            ],
        )
        assert group.max_date == date(2026, 3, 15)

    def test_max_date_no_dates(self):
        group = RoadmapGroup(
            name="G",
            stories=[_make_story(end_date=None)],
        )
        assert group.max_date is None

    def test_status_counts(self):
        group = RoadmapGroup(
            name="G",
            stories=[
                _make_story(id="A", status="BACKLOG"),
                _make_story(id="B", status="BACKLOG"),
                _make_story(id="C", status="EXECUCAO"),
                _make_story(id="D", status="CONCLUIDO"),
            ],
        )
        counts = group.status_counts
        assert counts["BACKLOG"] == 2
        assert counts["EXECUCAO"] == 1
        assert counts["CONCLUIDO"] == 1

    def test_status_counts_empty(self):
        group = RoadmapGroup(name="Empty")
        assert group.status_counts == {}

    def test_expanded_default_false(self):
        group = RoadmapGroup(name="G")
        assert group.expanded is False

    def test_feature_id_default_none(self):
        group = RoadmapGroup(name="G")
        assert group.feature_id is None


# --- T012b: Tests for RoadmapData.status_counts ---


class TestRoadmapData:
    def test_status_counts_aggregated(self):
        data = RoadmapData(
            groups=[
                RoadmapGroup(
                    name="G1",
                    stories=[
                        _make_story(id="A", status="BACKLOG"),
                        _make_story(id="B", status="EXECUCAO"),
                    ],
                ),
                RoadmapGroup(
                    name="G2",
                    stories=[
                        _make_story(id="C", status="BACKLOG"),
                        _make_story(id="D", status="CONCLUIDO"),
                    ],
                ),
            ],
            min_date=date(2026, 1, 1),
            max_date=date(2026, 3, 1),
            total_stories=4,
            scheduled_stories=4,
        )
        counts = data.status_counts
        assert counts["BACKLOG"] == 2
        assert counts["EXECUCAO"] == 1
        assert counts["CONCLUIDO"] == 1


# --- TestRoadmapViewModelInit ---


class TestRoadmapViewModelInit:
    def test_init_stores_container(self, viewmodel, mock_container):
        assert viewmodel._container is mock_container

    def test_init_empty_caches(self, viewmodel):
        assert viewmodel._cached_stories == []
        assert viewmodel._cached_features == {}


# --- T013: Tests for load_data with feature grouping ---


class TestLoadData:
    @pytest.mark.asyncio
    async def test_returns_roadmap_data(self, viewmodel, stories):
        result = await viewmodel.load_data()

        assert result is not None
        assert isinstance(result, RoadmapData)
        assert result.total_stories == 3
        assert result.scheduled_stories == 3
        assert result.min_date == date(2026, 1, 15)
        assert result.max_date == date(2026, 2, 15)

    @pytest.mark.asyncio
    async def test_groups_by_feature(self, viewmodel):
        result = await viewmodel.load_data()

        assert result is not None
        group_names = {g.name for g in result.groups}
        assert "Feature A" in group_names
        assert "Feature B" in group_names

    @pytest.mark.asyncio
    async def test_groups_sorted_by_start_date(self, viewmodel):
        result = await viewmodel.load_data()
        assert result is not None
        dates = [g.min_date for g in result.groups if g.min_date]
        assert dates == sorted(dates)

    @pytest.mark.asyncio
    async def test_groups_collapsed_by_default(self, viewmodel):
        result = await viewmodel.load_data()
        assert result is not None
        for group in result.groups:
            assert group.expanded is False

    @pytest.mark.asyncio
    async def test_returns_none_when_no_scheduled_stories(self, mock_list_features_uc):
        stories_no_dates = [
            _make_story(id="BACK-001", start_date=None, end_date=None),
            _make_story(id="BACK-002", start_date=None, end_date=None),
        ]
        uc = AsyncMock()
        uc.execute.return_value = stories_no_dates
        container = _make_mock_container(uc, mock_list_features_uc)
        vm = RoadmapViewModel(container)

        result = await vm.load_data()
        assert result is None

    @pytest.mark.asyncio
    async def test_caches_stories_after_load(self, viewmodel, stories):
        await viewmodel.load_data()
        assert len(viewmodel._cached_stories) == 3

    @pytest.mark.asyncio
    async def test_completion_percent_feature_a(self, viewmodel):
        result = await viewmodel.load_data()
        feature_a = next(g for g in result.groups if g.name == "Feature A")
        # 1 CONCLUIDO out of 2
        assert feature_a.completion_percent == 50.0

    @pytest.mark.asyncio
    async def test_stories_without_feature_go_to_sem_feature(
        self, mock_list_features_uc
    ):
        stories = [
            _make_story(id="BACK-001", feature_name=None, feature_id=None),
        ]
        uc = AsyncMock()
        uc.execute.return_value = stories
        container = _make_mock_container(uc, mock_list_features_uc)
        vm = RoadmapViewModel(container)

        result = await vm.load_data()
        assert result is not None
        assert any(g.name == "Sem feature" for g in result.groups)

    @pytest.mark.asyncio
    async def test_feature_group_has_correct_feature_id(self, viewmodel):
        result = await viewmodel.load_data()
        feature_a = next(g for g in result.groups if g.name == "Feature A")
        assert feature_a.feature_id == 1

    @pytest.mark.asyncio
    async def test_sem_feature_group_has_none_feature_id(self, mock_list_features_uc):
        stories = [
            _make_story(id="X-001", feature_name=None, feature_id=None),
        ]
        uc = AsyncMock()
        uc.execute.return_value = stories
        container = _make_mock_container(uc, mock_list_features_uc)
        vm = RoadmapViewModel(container)

        result = await vm.load_data()
        sem_feature = next(g for g in result.groups if g.name == "Sem feature")
        assert sem_feature.feature_id is None


# --- T014: Tests for toggle_group, apply_filters, clear_filters, get_available_filters ---


class TestToggleGroup:
    @pytest.mark.asyncio
    async def test_toggle_expands_group(self, viewmodel):
        await viewmodel.load_data()
        result = viewmodel.toggle_group("Feature A")
        feature_a = next(g for g in result.groups if g.name == "Feature A")
        assert feature_a.expanded is True

    @pytest.mark.asyncio
    async def test_toggle_twice_collapses(self, viewmodel):
        await viewmodel.load_data()
        viewmodel.toggle_group("Feature A")
        result = viewmodel.toggle_group("Feature A")
        feature_a = next(g for g in result.groups if g.name == "Feature A")
        assert feature_a.expanded is False

    @pytest.mark.asyncio
    async def test_toggle_preserves_other_groups(self, viewmodel):
        await viewmodel.load_data()
        result = viewmodel.toggle_group("Feature A")
        feature_b = next(g for g in result.groups if g.name == "Feature B")
        assert feature_b.expanded is False

    @pytest.mark.asyncio
    async def test_toggle_returns_valid_roadmap_data(self, viewmodel):
        await viewmodel.load_data()
        result = viewmodel.toggle_group("Feature A")
        assert isinstance(result, RoadmapData)
        assert result.total_stories == 3


class TestApplyFilters:
    @pytest.mark.asyncio
    async def test_filter_by_feature(self, viewmodel):
        await viewmodel.load_data()
        result = viewmodel.apply_filters(RoadmapFilters(feature="Feature A"))
        assert result.total_stories == 2
        group_names = {g.name for g in result.groups}
        assert "Feature A" in group_names

    @pytest.mark.asyncio
    async def test_filter_by_developer(self, viewmodel):
        await viewmodel.load_data()
        result = viewmodel.apply_filters(RoadmapFilters(developer="Dev A"))
        assert result.total_stories == 2

    @pytest.mark.asyncio
    async def test_filter_by_component(self, viewmodel):
        await viewmodel.load_data()
        result = viewmodel.apply_filters(RoadmapFilters(component="Frontend"))
        assert result.total_stories == 1

    @pytest.mark.asyncio
    async def test_filter_by_search_text(self, viewmodel):
        await viewmodel.load_data()
        result = viewmodel.apply_filters(RoadmapFilters(search_text="Story 3"))
        assert result.total_stories == 1

    @pytest.mark.asyncio
    async def test_filter_combined_and(self, viewmodel):
        await viewmodel.load_data()
        result = viewmodel.apply_filters(
            RoadmapFilters(feature="Feature A", component="Backend")
        )
        assert result.total_stories == 2

    @pytest.mark.asyncio
    async def test_filter_no_results(self, viewmodel):
        await viewmodel.load_data()
        result = viewmodel.apply_filters(RoadmapFilters(feature="Nonexistent"))
        assert result.total_stories == 0

    @pytest.mark.asyncio
    async def test_filter_preserves_group_expansion(self, viewmodel):
        await viewmodel.load_data()
        viewmodel.toggle_group("Feature A")
        result = viewmodel.apply_filters(RoadmapFilters(feature="Feature A"))
        feature_a = next(g for g in result.groups if g.name == "Feature A")
        assert feature_a.expanded is True


class TestClearFilters:
    @pytest.mark.asyncio
    async def test_clear_returns_all(self, viewmodel):
        await viewmodel.load_data()
        viewmodel.apply_filters(RoadmapFilters(feature="Feature A"))
        result = viewmodel.clear_filters()
        assert result.total_stories == 3

    @pytest.mark.asyncio
    async def test_clear_resets_filter_state(self, viewmodel):
        await viewmodel.load_data()
        viewmodel.apply_filters(RoadmapFilters(feature="Feature A"))
        viewmodel.clear_filters()
        assert viewmodel._current_filters.is_active is False


class TestGetAvailableFilters:
    @pytest.mark.asyncio
    async def test_returns_all_features(self, viewmodel):
        await viewmodel.load_data()
        filters = viewmodel.get_available_filters()
        assert "Feature A" in filters["features"]
        assert "Feature B" in filters["features"]

    @pytest.mark.asyncio
    async def test_returns_all_developers(self, viewmodel):
        await viewmodel.load_data()
        filters = viewmodel.get_available_filters()
        assert "Dev A" in filters["developers"]
        assert "Dev B" in filters["developers"]

    @pytest.mark.asyncio
    async def test_returns_all_components(self, viewmodel):
        await viewmodel.load_data()
        filters = viewmodel.get_available_filters()
        assert "Backend" in filters["components"]
        assert "Frontend" in filters["components"]

    @pytest.mark.asyncio
    async def test_nao_atribuido_for_null_developer(self, mock_list_features_uc):
        stories = [
            _make_story(id="X-001", developer_name=None, developer_id=None),
        ]
        uc = AsyncMock()
        uc.execute.return_value = stories
        container = _make_mock_container(uc, mock_list_features_uc)
        vm = RoadmapViewModel(container)
        await vm.load_data()

        filters = vm.get_available_filters()
        assert "Nao atribuido" in filters["developers"]

    @pytest.mark.asyncio
    async def test_stories_without_feature_not_in_features(self, mock_list_features_uc):
        stories = [
            _make_story(id="X-001", feature_name=None, feature_id=None),
        ]
        uc = AsyncMock()
        uc.execute.return_value = stories
        container = _make_mock_container(uc, mock_list_features_uc)
        vm = RoadmapViewModel(container)
        await vm.load_data()

        filters = vm.get_available_filters()
        assert filters["features"] == []
