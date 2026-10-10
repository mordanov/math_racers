from __future__ import annotations

import uuid

from app.child_profiles.models import ChildProfile
from app.child_profiles.repository import ChildProfileRepository
from app.shared.exceptions import ConflictError, NotFoundError, PermissionError

_MAX_PROFILES = 5


class ManageChildProfilesUseCase:
    def __init__(self, repository: ChildProfileRepository) -> None:
        self._repository = repository

    async def list_for_account(self, account_id: uuid.UUID) -> list[ChildProfile]:
        return await self._repository.list_for_account(account_id)

    async def create(self, account_id: uuid.UUID, display_name: str) -> ChildProfile:
        count = await self._repository.count_for_account(account_id)
        if count >= _MAX_PROFILES:
            raise ConflictError(
                "MAX_CHILD_PROFILES",
                f"Maximum of {_MAX_PROFILES} child profiles reached.",
            )
        return await self._repository.create(account_id, display_name)

    async def get_owned(self, account_id: uuid.UUID, profile_id: uuid.UUID) -> ChildProfile:
        profile = await self._repository.get(profile_id)
        if profile is None:
            raise NotFoundError("CHILD_PROFILE_NOT_FOUND", "Child profile not found.")
        if profile.account_id != account_id:
            raise PermissionError("FORBIDDEN", "Not your child profile.")
        return profile

    async def delete(self, account_id: uuid.UUID, profile_id: uuid.UUID) -> None:
        await self.get_owned(account_id, profile_id)
        await self._repository.delete(profile_id)
