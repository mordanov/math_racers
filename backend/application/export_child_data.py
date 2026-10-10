from __future__ import annotations

import uuid

from sqlalchemy import false, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.achievements.models import PlayerAchievement
from app.avatars.models import Avatar
from app.championships.models import Championship, ChampionshipRace
from app.progression.models import ChildProgression, XPEvent
from app.races.models import Race, RaceAnswer, RaceParticipant
from app.statistics.models import AvatarStats, RaceSession


class ExportChildDataUseCase:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def execute(
        self, account_id: uuid.UUID, child_profile_id: uuid.UUID
    ) -> dict[str, object]:
        avatars = await self._session.execute(
            select(Avatar)
            .where(
                Avatar.account_id == account_id,
                Avatar.child_profile_id == child_profile_id,
            )
            .options(selectinload(Avatar.portraits))
        )
        avatar_records = list(avatars.scalars().all())
        avatar_ids = [avatar.id for avatar in avatar_records]
        races = await self._session.execute(
            select(Race).where(
                Race.account_id == account_id,
                Race.child_profile_id == child_profile_id,
            )
        )
        statistics = await self._session.execute(
            select(RaceSession).where(
                RaceSession.account_id == account_id,
                RaceSession.child_profile_id == child_profile_id,
            )
        )
        avatar_statistics = await self._session.execute(
            select(AvatarStats).where(
                AvatarStats.account_id == account_id,
                AvatarStats.child_profile_id == child_profile_id,
                AvatarStats.avatar_id.in_(avatar_ids),
            )
            if avatar_ids
            else select(AvatarStats).where(false())
        )
        achievements = await self._session.execute(
            select(PlayerAchievement).where(
                PlayerAchievement.account_id == account_id,
                PlayerAchievement.child_profile_id == child_profile_id,
            )
        )
        progression = await self._session.execute(
            select(ChildProgression).where(
                ChildProgression.account_id == account_id,
                ChildProgression.child_profile_id == child_profile_id,
            )
        )
        xp_events = await self._session.execute(
            select(XPEvent).where(
                XPEvent.account_id == account_id,
                XPEvent.child_profile_id == child_profile_id,
            )
        )
        championships = await self._session.execute(
            select(Championship).where(
                Championship.account_id == account_id,
                Championship.child_profile_id == child_profile_id,
            )
        )
        race_records = list(races.scalars().all())
        championship_records = list(championships.scalars().all())
        race_ids = [race.id for race in race_records]
        championship_ids = [item.id for item in championship_records]

        answers = await self._session.execute(
            select(RaceAnswer).where(RaceAnswer.race_id.in_(race_ids))
            if race_ids
            else select(RaceAnswer).where(false())
        )
        participants = await self._session.execute(
            select(RaceParticipant).where(RaceParticipant.race_id.in_(race_ids))
            if race_ids
            else select(RaceParticipant).where(false())
        )
        championship_races = await self._session.execute(
            select(ChampionshipRace).where(ChampionshipRace.championship_id.in_(championship_ids))
            if championship_ids
            else select(ChampionshipRace).where(false())
        )

        return {
            "child_profile_id": str(child_profile_id),
            "avatars": [self._avatar_record(record) for record in avatar_records],
            "avatar_statistics": [
                {
                    "avatar_id": str(record.avatar_id),
                    "total_races": record.total_races,
                    "wins": record.wins,
                    "podiums": record.podiums,
                    "best_streak": record.best_streak,
                    "last_race_at": record.last_race_at.isoformat(),
                }
                for record in avatar_statistics.scalars().all()
            ],
            "races": [self._race_record(record) for record in race_records],
            "race_answers": [
                {
                    "id": str(record.id),
                    "race_id": str(record.race_id),
                    "operation": record.operation,
                    "is_correct": record.is_correct,
                    "response_time_ms": record.response_time_ms,
                }
                for record in answers.scalars().all()
            ],
            "race_participants": [
                {
                    "id": str(record.id),
                    "race_id": str(record.race_id),
                    "avatar_id": record.avatar_id,
                    "position": record.position,
                    "problems_correct": record.problems_correct,
                    "total_distance": record.total_distance,
                    "xp_earned": record.xp_earned,
                    "longest_streak": record.longest_streak,
                }
                for record in participants.scalars().all()
            ],
            "statistics": [
                {
                    "id": str(record.id),
                    "race_id": str(record.race_id) if record.race_id else None,
                    "mode": record.mode,
                    "problems_solved": record.problems_solved,
                    "correct_answers": record.correct_answers,
                    "xp_earned": record.xp_earned,
                    "finished_at": record.finished_at.isoformat(),
                }
                for record in statistics.scalars().all()
            ],
            "achievements": [
                {
                    "id": str(record.id),
                    "achievement_key": record.achievement_key,
                    "unlocked_at": record.unlocked_at.isoformat(),
                }
                for record in achievements.scalars().all()
            ],
            "progression": [
                {
                    "total_xp": record.total_xp,
                    "current_level": record.current_level,
                    "updated_at": record.updated_at.isoformat(),
                }
                for record in progression.scalars().all()
            ],
            "xp_events": [
                {
                    "id": str(record.id),
                    "source": record.source,
                    "amount": record.amount,
                    "race_id": str(record.race_id) if record.race_id else None,
                    "championship_id": (
                        str(record.championship_id) if record.championship_id else None
                    ),
                    "created_at": record.created_at.isoformat(),
                }
                for record in xp_events.scalars().all()
            ],
            "championships": [self._championship_record(record) for record in championship_records],
            "championship_races": [
                {
                    "id": str(record.id),
                    "championship_id": str(record.championship_id),
                    "race_id": str(record.race_id),
                    "race_index": record.race_index,
                    "avatar_id": record.avatar_id,
                    "finishing_position": record.finishing_position,
                    "points_earned": record.points_earned,
                }
                for record in championship_races.scalars().all()
            ],
        }

    @staticmethod
    def _avatar_record(record: Avatar) -> dict[str, object]:
        return {
            "id": str(record.id),
            "species": record.species,
            "name": record.name,
            "status": record.status,
            "created_at": record.created_at.isoformat(),
            "portraits": [
                {
                    "id": str(portrait.id),
                    "version": portrait.version,
                    "full_url": portrait.full_url,
                    "medium_url": portrait.medium_url,
                    "small_url": portrait.small_url,
                    "thumb_url": portrait.thumb_url,
                    "created_at": portrait.created_at.isoformat(),
                }
                for portrait in record.portraits
            ],
        }

    @staticmethod
    def _race_record(record: Race) -> dict[str, object]:
        return {
            "id": str(record.id),
            "mode": record.mode,
            "difficulty_tier": record.difficulty_tier,
            "status": record.status,
            "result_payload": record.result_payload,
            "result_response": record.result_response,
            "started_at": record.started_at.isoformat(),
            "completed_at": record.completed_at.isoformat(),
        }

    @staticmethod
    def _championship_record(record: Championship) -> dict[str, object]:
        return {
            "id": str(record.id),
            "total_races": record.total_races,
            "races_completed": record.races_completed,
            "status": record.status,
            "created_at": record.created_at.isoformat(),
        }
