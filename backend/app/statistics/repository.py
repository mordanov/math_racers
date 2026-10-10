from __future__ import annotations

import uuid
from datetime import datetime
from typing import Protocol

from sqlalchemy import case, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.avatars.models import Avatar
from app.races.models import Race, RaceAnswer
from app.statistics.models import AvatarStats, PlayerStats, RaceSession

PAGE_SIZE = 20


class StatisticsRepository(Protocol):
    async def get_player_stats(self, account_id: uuid.UUID) -> PlayerStats | None: ...
    async def get_player_stats_for_child(
        self, account_id: uuid.UUID, child_profile_id: uuid.UUID
    ) -> PlayerStats | None: ...

    async def get_operation_counts(
        self,
        account_id: uuid.UUID,
        child_profile_id: uuid.UUID,
        since: datetime | None = None,
    ) -> dict[str, tuple[int, int]]: ...

    async def upsert_player_stats(
        self,
        account_id: uuid.UUID,
        *,
        races_delta: int,
        problems_delta: int,
        correct_delta: int,
        response_ms_delta: int,
        streak: int,
    ) -> None: ...

    async def get_avatar_stats(
        self, account_id: uuid.UUID, child_profile_id: uuid.UUID, avatar_id: uuid.UUID
    ) -> AvatarStats | None: ...

    async def get_avatar_stats_for_player(self, account_id: uuid.UUID) -> list[AvatarStats]: ...

    async def upsert_avatar_stats(
        self,
        avatar_id: uuid.UUID,
        account_id: uuid.UUID,
        child_profile_id: uuid.UUID | None,
        *,
        wins_delta: int,
        podiums_delta: int,
        streak: int,
    ) -> None: ...

    async def insert_session(
        self,
        account_id: uuid.UUID,
        child_profile_id: uuid.UUID | None,
        avatar_id: uuid.UUID,
        race_id: uuid.UUID | None,
        mode: str,
        finishing_position: int | None,
        problems_solved: int,
        correct_answers: int,
        difficulty_tier: int,
        xp_earned: int,
        avg_response_ms: int,
        longest_streak: int,
        started_at: datetime,
        finished_at: datetime,
    ) -> None: ...

    async def get_history(
        self, account_id: uuid.UUID, page: int, child_profile_id: uuid.UUID | None = None
    ) -> tuple[list[RaceSession], int]: ...

    async def get_sessions_since(
        self, account_id: uuid.UUID, since: datetime, child_profile_id: uuid.UUID | None = None
    ) -> list[RaceSession]: ...

    async def get_all_sessions(
        self, account_id: uuid.UUID, child_profile_id: uuid.UUID | None = None
    ) -> list[RaceSession]: ...

    async def get_best_race_accuracy(
        self, account_id: uuid.UUID, child_profile_id: uuid.UUID | None = None
    ) -> float | None: ...

    async def get_fastest_avg_response_ms(
        self, account_id: uuid.UUID, child_profile_id: uuid.UUID | None = None
    ) -> int | None: ...


class SQLAlchemyStatisticsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_player_stats(self, account_id: uuid.UUID) -> PlayerStats | None:
        result = await self._session.execute(
            select(PlayerStats).where(PlayerStats.account_id == account_id)
        )
        return result.scalar_one_or_none()

    async def get_player_stats_for_child(
        self, account_id: uuid.UUID, child_profile_id: uuid.UUID
    ) -> PlayerStats | None:
        result = await self._session.execute(
            select(
                func.count(RaceSession.id).label("total_races"),
                func.coalesce(func.sum(RaceSession.problems_solved), 0).label(
                    "total_problems_solved"
                ),
                func.coalesce(func.sum(RaceSession.correct_answers), 0).label("correct_answers"),
                func.coalesce(
                    func.sum(RaceSession.avg_response_ms * RaceSession.problems_solved), 0
                ).label("total_response_ms"),
                func.coalesce(func.max(RaceSession.longest_streak), 0).label("best_streak"),
                func.max(RaceSession.finished_at).label("updated_at"),
            ).where(
                RaceSession.account_id == account_id,
                RaceSession.child_profile_id == child_profile_id,
            )
        )
        row = result.one()
        if row.total_races == 0:
            return None
        return PlayerStats(
            account_id=account_id,
            total_races=row.total_races,
            total_problems_solved=row.total_problems_solved,
            correct_answers=row.correct_answers,
            total_response_ms=row.total_response_ms,
            best_streak=row.best_streak,
            updated_at=row.updated_at,
        )

    async def get_operation_counts(
        self,
        account_id: uuid.UUID,
        child_profile_id: uuid.UUID,
        since: datetime | None = None,
    ) -> dict[str, tuple[int, int]]:
        statement = (
            select(
                RaceAnswer.operation,
                func.count(RaceAnswer.id).label("attempts"),
                func.sum(case((RaceAnswer.is_correct.is_(True), 1), else_=0)).label("correct"),
            )
            .join(Race, Race.id == RaceAnswer.race_id)
            .where(
                Race.account_id == account_id,
                Race.child_profile_id == child_profile_id,
            )
            .group_by(RaceAnswer.operation)
        )
        if since is not None:
            statement = statement.where(Race.completed_at >= since)
        result = await self._session.execute(statement)
        return {row.operation: (int(row.attempts), int(row.correct)) for row in result.all()}

    async def upsert_player_stats(
        self,
        account_id: uuid.UUID,
        *,
        races_delta: int,
        problems_delta: int,
        correct_delta: int,
        response_ms_delta: int,
        streak: int,
    ) -> None:
        await self._session.execute(
            text("""
                INSERT INTO player_stats
                    (account_id, total_races, total_problems_solved, correct_answers,
                     total_response_ms, best_streak, updated_at)
                VALUES
                    (:account_id, :races, :problems, :correct, :response_ms, :streak, now())
                ON CONFLICT (account_id) DO UPDATE
                SET total_races            = player_stats.total_races + EXCLUDED.total_races,
                    total_problems_solved  = player_stats.total_problems_solved + EXCLUDED.total_problems_solved,
                    correct_answers        = player_stats.correct_answers + EXCLUDED.correct_answers,
                    total_response_ms      = player_stats.total_response_ms + EXCLUDED.total_response_ms,
                    best_streak            = GREATEST(player_stats.best_streak, EXCLUDED.best_streak),
                    updated_at             = now()
            """),
            {
                "account_id": str(account_id),
                "races": races_delta,
                "problems": problems_delta,
                "correct": correct_delta,
                "response_ms": response_ms_delta,
                "streak": streak,
            },
        )

    async def get_avatar_stats(
        self, account_id: uuid.UUID, child_profile_id: uuid.UUID, avatar_id: uuid.UUID
    ) -> AvatarStats | None:
        result = await self._session.execute(
            select(AvatarStats)
            .join(Avatar, Avatar.id == AvatarStats.avatar_id)
            .where(
                AvatarStats.avatar_id == avatar_id,
                AvatarStats.child_profile_id == child_profile_id,
                Avatar.account_id == account_id,
                Avatar.child_profile_id == child_profile_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_avatar_stats_for_player(self, account_id: uuid.UUID) -> list[AvatarStats]:
        result = await self._session.execute(
            select(AvatarStats).where(AvatarStats.account_id == account_id)
        )
        return list(result.scalars().all())

    async def upsert_avatar_stats(
        self,
        avatar_id: uuid.UUID,
        account_id: uuid.UUID,
        child_profile_id: uuid.UUID | None,
        *,
        wins_delta: int,
        podiums_delta: int,
        streak: int,
    ) -> None:
        await self._session.execute(
            text("""
                INSERT INTO avatar_stats
                    (avatar_id, account_id, child_profile_id, total_races, wins, podiums,
                     best_streak, last_race_at)
                VALUES
                    (:avatar_id, :account_id, :child_profile_id, 1, :wins, :podiums, :streak, now())
                ON CONFLICT (avatar_id, child_profile_id) DO UPDATE
                SET total_races  = avatar_stats.total_races + 1,
                    wins         = avatar_stats.wins + EXCLUDED.wins,
                    podiums      = avatar_stats.podiums + EXCLUDED.podiums,
                    best_streak  = GREATEST(avatar_stats.best_streak, EXCLUDED.best_streak),
                    last_race_at = now()
            """),
            {
                "avatar_id": str(avatar_id),
                "account_id": str(account_id),
                "child_profile_id": str(child_profile_id),
                "wins": wins_delta,
                "podiums": podiums_delta,
                "streak": streak,
            },
        )

    async def insert_session(
        self,
        account_id: uuid.UUID,
        child_profile_id: uuid.UUID | None,
        avatar_id: uuid.UUID,
        race_id: uuid.UUID | None,
        mode: str,
        finishing_position: int | None,
        problems_solved: int,
        correct_answers: int,
        difficulty_tier: int,
        xp_earned: int,
        avg_response_ms: int,
        longest_streak: int,
        started_at: datetime,
        finished_at: datetime,
    ) -> None:
        session = RaceSession(
            account_id=account_id,
            child_profile_id=child_profile_id,
            avatar_id=avatar_id,
            race_id=race_id,
            mode=mode,
            finishing_position=finishing_position,
            problems_solved=problems_solved,
            correct_answers=correct_answers,
            difficulty_tier=difficulty_tier,
            xp_earned=xp_earned,
            avg_response_ms=avg_response_ms,
            longest_streak=longest_streak,
            started_at=started_at,
            finished_at=finished_at,
        )
        self._session.add(session)
        await self._session.flush()

    async def get_history(
        self, account_id: uuid.UUID, page: int, child_profile_id: uuid.UUID | None = None
    ) -> tuple[list[RaceSession], int]:
        conditions = [RaceSession.account_id == account_id]
        if child_profile_id is not None:
            conditions.append(RaceSession.child_profile_id == child_profile_id)
        total_result = await self._session.execute(select(func.count()).where(*conditions))
        total = total_result.scalar_one()

        offset = (page - 1) * PAGE_SIZE
        result = await self._session.execute(
            select(RaceSession)
            .where(*conditions)
            .order_by(RaceSession.finished_at.desc())
            .offset(offset)
            .limit(PAGE_SIZE)
        )
        return list(result.scalars().all()), total

    async def get_sessions_since(
        self, account_id: uuid.UUID, since: datetime, child_profile_id: uuid.UUID | None = None
    ) -> list[RaceSession]:
        conditions = [
            RaceSession.account_id == account_id,
            RaceSession.finished_at >= since,
        ]
        if child_profile_id is not None:
            conditions.append(RaceSession.child_profile_id == child_profile_id)
        result = await self._session.execute(
            select(RaceSession).where(*conditions).order_by(RaceSession.finished_at.desc())
        )
        return list(result.scalars().all())

    async def get_all_sessions(
        self, account_id: uuid.UUID, child_profile_id: uuid.UUID | None = None
    ) -> list[RaceSession]:
        conditions = [RaceSession.account_id == account_id]
        if child_profile_id is not None:
            conditions.append(RaceSession.child_profile_id == child_profile_id)
        result = await self._session.execute(
            select(RaceSession).where(*conditions).order_by(RaceSession.finished_at.desc())
        )
        return list(result.scalars().all())

    async def get_best_race_accuracy(
        self, account_id: uuid.UUID, child_profile_id: uuid.UUID | None = None
    ) -> float | None:
        statement = text("""
                SELECT MAX(correct_answers::float / NULLIF(problems_solved, 0))
                FROM race_sessions
                WHERE account_id = :account_id
                  AND (:child_profile_id IS NULL OR child_profile_id = :child_profile_id)
            """)
        result = await self._session.execute(
            statement,
            {
                "account_id": str(account_id),
                "child_profile_id": str(child_profile_id) if child_profile_id else None,
            },
        )
        value = result.scalar_one_or_none()
        return float(value) if value is not None else None

    async def get_fastest_avg_response_ms(
        self, account_id: uuid.UUID, child_profile_id: uuid.UUID | None = None
    ) -> int | None:
        conditions = [RaceSession.account_id == account_id]
        if child_profile_id is not None:
            conditions.append(RaceSession.child_profile_id == child_profile_id)
        result = await self._session.execute(
            select(func.min(RaceSession.avg_response_ms)).where(*conditions)
        )
        value = result.scalar_one_or_none()
        return int(value) if value is not None else None
