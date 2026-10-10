from __future__ import annotations

import uuid

from sqlalchemy import bindparam, text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.child_profiles.schemas import LegacyRecordAssignment
from app.shared.exceptions import ConflictError, ValidationError

_TABLES = {
    "avatar": "avatars",
    "avatar_stats": "avatar_stats",
    "achievement": "player_achievements",
    "race": "races",
    "statistics": "race_sessions",
    "xp_event": "xp_events",
    "championship": "championships",
}
_LEGACY_SELECTS = {
    "avatar": ("avatars", "COALESCE(name, species)"),
    "avatar_stats": ("avatar_stats", "avatar_id::text"),
    "achievement": ("player_achievements", "achievement_key"),
    "race": ("races", "mode"),
    "statistics": ("race_sessions", "mode"),
    "xp_event": ("xp_events", "source"),
    "championship": ("championships", "status"),
}


class AssignLegacyChildDataUseCase:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_unassigned(self, account_id: uuid.UUID) -> list[dict[str, str]]:
        result: list[dict[str, str]] = []
        progressions = await self._session.execute(
            text("""
                SELECT account_id AS id, total_xp::text AS label
                FROM player_progressions
                WHERE account_id = :account_id
                  AND assigned_child_profile_id IS NULL
                """),
            {"account_id": str(account_id)},
        )
        result.extend(
            {
                "record_type": "progression",
                "record_id": str(row.id),
                "label": f"{row.label} XP",
            }
            for row in progressions
        )
        for record_type, (table, label_expression) in _LEGACY_SELECTS.items():
            rows = await self._session.execute(
                text(f"""
                    SELECT id, {label_expression} AS label
                    FROM {table}
                    WHERE account_id = :account_id AND child_profile_id IS NULL
                    ORDER BY id
                    """),
                {"account_id": str(account_id)},
            )
            result.extend(
                {
                    "record_type": record_type,
                    "record_id": str(row.id),
                    "label": str(row.label),
                }
                for row in rows
            )
        return result

    async def execute(
        self,
        account_id: uuid.UUID,
        child_profile_id: uuid.UUID,
        records: list[LegacyRecordAssignment],
    ) -> int:
        assigned = 0
        progression_ids = [
            record.record_id for record in records if record.record_type == "progression"
        ]
        if progression_ids:
            if len(progression_ids) != 1 or progression_ids[0] != account_id:
                raise ValidationError(
                    "LEGACY_RECORD_ASSIGNMENT_INVALID",
                    "The progression record must identify the parent account.",
                )
            progression = await self._session.execute(
                text("""
                    UPDATE player_progressions
                    SET assigned_child_profile_id = :child_profile_id
                    WHERE account_id = :account_id
                      AND assigned_child_profile_id IS NULL
                    RETURNING total_xp
                    """),
                {
                    "child_profile_id": str(child_profile_id),
                    "account_id": str(account_id),
                },
            )
            row = progression.one_or_none()
            if row is None:
                raise ConflictError(
                    "LEGACY_RECORD_ASSIGNMENT_CONFLICT",
                    "One or more records are not unassigned records owned by this account.",
                )
            await self._session.execute(
                text("""
                    INSERT INTO child_progressions
                        (child_profile_id, account_id, total_xp, current_level, updated_at)
                    VALUES (
                        :child_profile_id,
                        :account_id,
                        :legacy_xp,
                        GREATEST(
                            1,
                            FLOOR(SQRT(CAST(:legacy_xp_for_level AS numeric) / 100))
                        )::integer,
                        now()
                    )
                    ON CONFLICT (child_profile_id) DO UPDATE
                    SET total_xp = child_progressions.total_xp + EXCLUDED.total_xp,
                        current_level = GREATEST(
                            1,
                            FLOOR(SQRT(
                                (child_progressions.total_xp + EXCLUDED.total_xp)::numeric / 100
                            ))
                        )::integer,
                        updated_at = now()
                    """),
                {
                    "child_profile_id": str(child_profile_id),
                    "account_id": str(account_id),
                    "legacy_xp": row.total_xp,
                    "legacy_xp_for_level": row.total_xp,
                },
            )
            assigned += 1

        for record_type, table in _TABLES.items():
            record_ids = [
                record.record_id for record in records if record.record_type == record_type
            ]
            if not record_ids:
                continue

            result = await self._session.execute(
                text(f"""
                    UPDATE {table}
                    SET child_profile_id = :child_profile_id
                    WHERE account_id = :account_id
                      AND child_profile_id IS NULL
                      AND id = ANY(:record_ids)
                    RETURNING id
                    """).bindparams(bindparam("record_ids", type_=ARRAY(UUID(as_uuid=True)))),
                {
                    "child_profile_id": str(child_profile_id),
                    "account_id": str(account_id),
                    "record_ids": record_ids,
                },
            )
            rows = result.fetchall()
            if len(rows) != len(record_ids):
                raise ConflictError(
                    "LEGACY_RECORD_ASSIGNMENT_CONFLICT",
                    "One or more records are not unassigned records owned by this account.",
                )
            assigned += len(rows)

        if assigned != len(records):
            raise ValidationError(
                "LEGACY_RECORD_ASSIGNMENT_INVALID",
                "Not all requested legacy records could be assigned.",
            )
        return assigned
