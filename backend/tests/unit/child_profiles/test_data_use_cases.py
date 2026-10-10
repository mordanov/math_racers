from __future__ import annotations

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.child_profiles.schemas import LegacyRecordAssignment
from app.shared.exceptions import ConflictError
from application.assign_legacy_child_data import AssignLegacyChildDataUseCase
from application.export_child_data import ExportChildDataUseCase

pytestmark = pytest.mark.unit


def test_legacy_progression_is_a_supported_assignable_record() -> None:
    record = LegacyRecordAssignment(record_type="progression", record_id=uuid.uuid4())

    assert record.record_type == "progression"


def _result(returned_ids: int) -> MagicMock:
    result = MagicMock()
    result.fetchall.return_value = [object() for _ in range(returned_ids)]
    return result


@pytest.mark.asyncio
async def test_legacy_assignment_requires_every_record_to_be_unassigned_and_owned() -> None:
    session = MagicMock()
    session.execute = AsyncMock(return_value=_result(0))
    records = [
        LegacyRecordAssignment(record_type="avatar", record_id=uuid.uuid4()),
    ]

    with pytest.raises(ConflictError, match="One or more records"):
        await AssignLegacyChildDataUseCase(session).execute(uuid.uuid4(), uuid.uuid4(), records)


@pytest.mark.asyncio
async def test_legacy_assignment_returns_count_after_all_updates_succeed() -> None:
    session = MagicMock()
    session.execute = AsyncMock(side_effect=[_result(1), _result(1)])
    records = [
        LegacyRecordAssignment(record_type="avatar", record_id=uuid.uuid4()),
        LegacyRecordAssignment(record_type="xp_event", record_id=uuid.uuid4()),
    ]

    assigned = await AssignLegacyChildDataUseCase(session).execute(
        uuid.uuid4(), uuid.uuid4(), records
    )

    assert assigned == len(records)
    assert session.execute.await_count == 2


@pytest.mark.asyncio
async def test_legacy_avatar_statistics_can_be_assigned_to_a_child() -> None:
    session = MagicMock()
    session.execute = AsyncMock(return_value=_result(1))
    records = [
        LegacyRecordAssignment(record_type="avatar_stats", record_id=uuid.uuid4()),
    ]

    assigned = await AssignLegacyChildDataUseCase(session).execute(
        uuid.uuid4(), uuid.uuid4(), records
    )

    assert assigned == 1
    query = str(session.execute.await_args.args[0])
    assert "UPDATE avatar_stats" in query
    assert "child_profile_id IS NULL" in query


@pytest.mark.asyncio
async def test_legacy_progression_assignment_merges_xp_into_child_progression() -> None:
    progression_result = MagicMock()
    progression_result.one_or_none.return_value = SimpleNamespace(total_xp=450)
    session = MagicMock()
    session.execute = AsyncMock(side_effect=[progression_result, MagicMock()])
    account_id = uuid.uuid4()
    child_profile_id = uuid.uuid4()
    records = [LegacyRecordAssignment(record_type="progression", record_id=account_id)]

    assigned = await AssignLegacyChildDataUseCase(session).execute(
        account_id, child_profile_id, records
    )

    assert assigned == 1
    update_query = str(session.execute.await_args_list[0].args[0])
    merge_query = str(session.execute.await_args_list[1].args[0])
    assert "UPDATE player_progressions" in update_query
    assert "assigned_child_profile_id IS NULL" in update_query
    assert "INSERT INTO child_progressions" in merge_query
    assert "child_progressions.total_xp + EXCLUDED.total_xp" in merge_query


@pytest.mark.asyncio
async def test_child_export_returns_empty_child_scoped_collections() -> None:
    empty_result = MagicMock()
    empty_result.scalars.return_value.all.return_value = []
    session = MagicMock()
    session.execute = AsyncMock(return_value=empty_result)

    export = await ExportChildDataUseCase(session).execute(uuid.uuid4(), uuid.uuid4())

    assert export["avatars"] == []
    assert export["races"] == []
    assert export["statistics"] == []
    assert export["achievements"] == []
    assert export["xp_events"] == []
    assert export["championships"] == []
