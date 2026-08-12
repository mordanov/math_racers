from __future__ import annotations

from dataclasses import dataclass

VALID_CATEGORIES = frozenset(
    {
        "racing",
        "mathematics",
        "streaks",
        "collection",
        "social",
        "milestones",
        "exploration",
        "special",
    }
)


@dataclass(frozen=True)
class AchievementDef:
    key: str
    category: str
    title: str
    description: str
    hidden: bool
    icon_path: str


CATALOGUE: list[AchievementDef] = [
    AchievementDef(
        key="first_race",
        category="racing",
        title="Off to the Races!",
        description="Complete your first race.",
        hidden=False,
        icon_path="assets/achievements/first_race.png",
    ),
    AchievementDef(
        key="perfect_race",
        category="mathematics",
        title="Perfect Score",
        description="Answer all 8 problems correctly in a single race.",
        hidden=False,
        icon_path="assets/achievements/perfect_race.png",
    ),
    AchievementDef(
        key="podium_finisher",
        category="racing",
        title="Podium Finisher",
        description="Finish in the top 3 in a race.",
        hidden=False,
        icon_path="assets/achievements/podium_finisher.png",
    ),
    AchievementDef(
        key="champion",
        category="racing",
        title="Champion",
        description="Finish in 1st place in a race.",
        hidden=False,
        icon_path="assets/achievements/champion.png",
    ),
    AchievementDef(
        key="level_5",
        category="milestones",
        title="Rising Star",
        description="Reach level 5.",
        hidden=False,
        icon_path="assets/achievements/level_5.png",
    ),
    AchievementDef(
        key="level_10",
        category="milestones",
        title="Veteran Racer",
        description="Reach level 10.",
        hidden=False,
        icon_path="assets/achievements/level_10.png",
    ),
    AchievementDef(
        key="level_20",
        category="milestones",
        title="Math Legend",
        description="Reach level 20.",
        hidden=False,
        icon_path="assets/achievements/level_20.png",
    ),
    AchievementDef(
        key="hidden_speedster",
        category="special",
        title="Speed Demon",
        description="Win a race with an average response time under 500ms.",
        hidden=True,
        icon_path="assets/achievements/hidden_speedster.png",
    ),
]

_CATALOGUE_BY_KEY: dict[str, AchievementDef] = {a.key: a for a in CATALOGUE}


def get_by_key(key: str) -> AchievementDef | None:
    return _CATALOGUE_BY_KEY.get(key)
