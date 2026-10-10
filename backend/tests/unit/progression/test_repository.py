from __future__ import annotations

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.progression.repository import SQLAlchemyProgressionRepository


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("child_profile_id", "table", "conflict_key"),
    [
        (None, "player_progressions", "account_id"),
        (uuid.uuid4(), "child_progressions", "child_profile_id"),
    ],
)
async def test_add_xp_increments_total_atomically_and_returns_saved_progression(
    child_profile_id: uuid.UUID | None, table: str, conflict_key: str
) -> None:
    session = MagicMock()
    result = MagicMock()
    result.one.return_value = SimpleNamespace(total_xp=700, current_level=2)
    session.execute = AsyncMock(return_value=result)
    account_id = uuid.uuid4()

    progression = await SQLAlchemyProgressionRepository(session).add_xp(
        account_id, 500, child_profile_id
    )

    query = str(session.execute.await_args.args[0])
    assert f"INSERT INTO {table}" in query
    assert f"ON CONFLICT ({conflict_key})" in query
    assert f"{table}.total_xp + EXCLUDED.total_xp" in query
    assert "CAST(:amount_for_level AS numeric)" in query
    assert "RETURNING total_xp, current_level" in query
    assert session.execute.await_args.args[1]["amount_for_level"] == 500
    assert progression == (700, 2)
    result.one.assert_called_once()
